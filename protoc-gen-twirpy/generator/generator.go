package generator

import (
	"bytes"
	"fmt"
	"path"
	"strings"

	plugin_go "github.com/golang/protobuf/protoc-gen-go/plugin"
	"github.com/pseudomuto/protokit"
	"google.golang.org/protobuf/proto"
)

type Plugin struct {
	messagesToFiles map[string]string
}

func (p *Plugin) Generate(r *plugin_go.CodeGeneratorRequest) (*plugin_go.CodeGeneratorResponse, error) {
	resp := &plugin_go.CodeGeneratorResponse{}
	resp.SupportedFeatures = proto.Uint64(uint64(plugin_go.CodeGeneratorResponse_FEATURE_PROTO3_OPTIONAL))

	files := protokit.ParseCodeGenRequest(r)
	p.messagesToFiles = buildMessagesToFiles(files)

	for _, fd := range files {
		templateVars, err := p.buildTwirpDescription(fd)
		if err != nil {
			return nil, fmt.Errorf("File[" + fd.GetName() + "][generate]: " + err.Error())
		}

		twirpFile, err := generateTwirpFile(templateVars)
		if err != nil {
			return nil, fmt.Errorf("File[" + fd.GetName() + "][generate]: " + err.Error())
		}
		resp.File = append(resp.File, twirpFile)

		pyiFile, err := generatePyiFile(templateVars)
		if err != nil {
			return nil, fmt.Errorf("File[" + fd.GetName() + "][generate]: " + err.Error())
		}
		resp.File = append(resp.File, pyiFile)
	}
	return resp, nil
}

func (p *Plugin) buildTwirpDescription(fd *protokit.FileDescriptor) (*TwirpTemplateVariables, error) {
	vars := &TwirpTemplateVariables{
		FileName: fd.GetName(),
	}

	imports := newImportBuilder(p.messagesToFiles)
	for _, svc := range fd.GetServices() {
		svcURL := fmt.Sprintf("%s.%s", fd.GetPackage(), svc.GetName())
		twirpSvc := &TwirpService{
			Name:       svc.GetName(),
			ServiceURL: svcURL,
		}

		for _, method := range svc.Methods {
			qualifiedInput, err := imports.addImportAndQualify(method.GetInputType())
			if err != nil {
				return nil, err
			}

			qualifiedOutput, err := imports.addImportAndQualify(method.GetOutputType())
			if err != nil {
				return nil, err
			}

			twirpMethod := &TwirpMethod{
				ServiceURL:      svcURL,
				ServiceName:     twirpSvc.Name,
				Name:            method.GetName(),
				Input:           getSymbol(method.GetInputType()),
				Output:          getSymbol(method.GetOutputType()),
				QualifiedInput:  qualifiedInput,
				QualifiedOutput: qualifiedOutput,
			}

			twirpSvc.Methods = append(twirpSvc.Methods, twirpMethod)
		}

		vars.Services = append(vars.Services, twirpSvc)
		for _, importStmt := range imports.imports {
			vars.Imports = append(vars.Imports, importStmt)
		}
	}
	return vars, nil
}

func generateTwirpFile(vars *TwirpTemplateVariables) (*plugin_go.CodeGeneratorResponse_File, error) {
	var buf = &bytes.Buffer{}
	err := TwirpTemplate.Execute(buf, vars)
	if err != nil {
		return nil, err
	}

	resp := &plugin_go.CodeGeneratorResponse_File{
		Name:    proto.String(strings.TrimSuffix(vars.FileName, path.Ext(vars.FileName)) + "_twirp.py"),
		Content: proto.String(buf.String()),
	}

	return resp, nil
}

func generatePyiFile(vars *TwirpTemplateVariables) (*plugin_go.CodeGeneratorResponse_File, error) {
	var buf = &bytes.Buffer{}
	err := PyiTwirpTemplate.Execute(buf, vars)
	if err != nil {
		return nil, err
	}

	resp := &plugin_go.CodeGeneratorResponse_File{
		Name:    proto.String(strings.TrimSuffix(vars.FileName, path.Ext(vars.FileName)) + "_twirp.pyi"),
		Content: proto.String(buf.String()),
	}

	return resp, nil
}

type importBuilder struct {
	seenAliases    map[string]struct{}
	aliasMappings  map[string]string
	imports        map[string]*TwirpImport
	messagesToFile map[string]string
}

func newImportBuilder(messagesToFile map[string]string) *importBuilder {
	return &importBuilder{
		messagesToFile: messagesToFile,
		seenAliases:    make(map[string]struct{}),
		aliasMappings:  make(map[string]string),
		imports:        make(map[string]*TwirpImport),
	}
}

func (ib *importBuilder) addImportAndQualify(typeToImport string) (string, error) {
	message := getSymbol(typeToImport)

	if file, ok := ib.messagesToFile[message]; ok {
		pyFile := asPythonPath(file)

		pathSlice := strings.Split(pyFile, ".")
		path := strings.Join(pathSlice[:len(pathSlice)-1], ".")
		module := pathSlice[len(pathSlice)-1]
		if _, present := ib.imports[pyFile]; !present {
			alias := ib.generateAlias(module)
			ib.aliasMappings[pyFile] = alias
			ib.imports[pyFile] = &TwirpImport{
				From:   path,
				Import: module,
				Alias:  alias,
			}
		}
		return ib.aliasMappings[pyFile] + "." + getMessageName(message), nil
	}
	return "", fmt.Errorf("cannot map message %s to a file", message)
}

func (ib *importBuilder) generateAlias(module string) string {
	alias := "_" + module

	for {
		if _, present := ib.seenAliases[alias]; !present {
			break
		}
		alias = "_" + alias
	}

	ib.seenAliases[alias] = struct{}{}
	return alias
}

func getSymbol(name string) string {
	return strings.TrimPrefix(name, ".")
}

func getMessageName(name string) string {
	parts := strings.Split(name, ".")
	return parts[len(parts)-1]
}

func asPythonPath(fileName string) string {
	asPath := strings.ReplaceAll(fileName, "/", ".")
	return strings.Replace(asPath, ".proto", "_pb2", 1)
}

func buildMessagesToFiles(fs []*protokit.FileDescriptor) map[string]string {
	mapOut := make(map[string]string)
	for _, fd := range fs {
		for _, msg := range fd.GetMessages() {
			mapOut[msg.GetPackage()+"."+msg.GetName()] = fd.GetName()
		}
	}
	return mapOut
}
