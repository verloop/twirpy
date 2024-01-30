package generator

import (
	"bytes"
	"fmt"
	"path"
	"strings"

    "github.com/pseudomuto/protokit"
	plugin_go "github.com/golang/protobuf/protoc-gen-go/plugin"
	"google.golang.org/protobuf/proto"
)

type Plugin struct {}

func (p *Plugin) Generate(r *plugin_go.CodeGeneratorRequest) (*plugin_go.CodeGeneratorResponse, error) {
	resp := &plugin_go.CodeGeneratorResponse{}
	resp.SupportedFeatures = proto.Uint64(uint64(plugin_go.CodeGeneratorResponse_FEATURE_PROTO3_OPTIONAL))

	files := protokit.ParseCodeGenRequest(r)
	for _, fd := range files {
		twirpFile, err := GenerateTwirpFile(fd)
		if err != nil {
			return nil, fmt.Errorf("File[" + fd.GetName() + "][generate]: " + err.Error())
		}
		resp.File = append(resp.File, twirpFile)
	}
	return resp, nil
}

func GenerateTwirpFile(fd *protokit.FileDescriptor) (*plugin_go.CodeGeneratorResponse_File, error) {

	name := fd.GetName()

	vars := TwirpTemplateVariables{
		FileName: name,
	}

	svcs := fd.GetServices()
	for _, svc := range svcs {
		svcURL := fmt.Sprintf("%s.%s", fd.GetPackage(), svc.GetName())
		twirpSvc := &TwirpService{
			Name:       svc.GetName(),
			ServiceURL: svcURL,
		}

		for _, method := range svc.Methods {
			twirpMethod := &TwirpMethod{
				ServiceURL:  svcURL,
				ServiceName: twirpSvc.Name,
				Name:        method.GetName(),
				Input:       getSymbol(method.GetInputType()),
				Output:      getSymbol(method.GetOutputType()),
			}

			twirpSvc.Methods = append(twirpSvc.Methods, twirpMethod)
		}
		vars.Services = append(vars.Services, twirpSvc)
	}

	var buf = &bytes.Buffer{}
	err := TwirpTemplate.Execute(buf, vars)
	if err != nil {
		return nil, err
	}

	resp := &plugin_go.CodeGeneratorResponse_File{
		Name:    proto.String(strings.TrimSuffix(name, path.Ext(name)) + "_twirp.py"),
		Content: proto.String(buf.String()),
	}

	return resp, nil
}

func getSymbol(name string) string {
	return strings.TrimPrefix(name, ".")
}
