package main

import (
	"bytes"
	"errors"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"path"
	"strings"

	"github.com/golang/protobuf/proto"
	"github.com/golang/protobuf/protoc-gen-go/descriptor"
	plugin "github.com/golang/protobuf/protoc-gen-go/plugin"
	"github.com/verloop/twirpy/protoc-gen-twirpy/source/templates"
)

func main() {
	data, err := ioutil.ReadAll(os.Stdin)
	if err != nil {
		log.Fatalln("Could not read from stdin", err)
		return
	}
	var req = &plugin.CodeGeneratorRequest{}
	err = proto.Unmarshal(data, req)
	if err != nil {
		log.Fatalln("Could not unmarshal proto", err)
		return
	}
	if len(req.GetFileToGenerate()) == 0 {
		log.Fatalln("No files to generate")
		return
	}
	resp := Generate(req)

	if resp == nil {
		resp = &plugin.CodeGeneratorResponse{}
	}

	data, err = proto.Marshal(resp)
	if err != nil {
		log.Fatalln("Could not unmarshal response proto", err)
	}
	_, err = os.Stdout.Write(data)
	if err != nil {
		log.Fatalln("Could not write response to stdout", err)
	}
}

func Generate(r *plugin.CodeGeneratorRequest) *plugin.CodeGeneratorResponse {
	resp := &plugin.CodeGeneratorResponse{}

	files := r.GetFileToGenerate()
	for _, fileName := range files {
		fd, err := getFileDescriptor(r.GetProtoFile(), fileName)
		if err != nil {
			resp.Error = proto.String("File[" + fileName + "][descriptor]: " + err.Error())
			return resp
		}

		twirpFile, err := GenerateTwirpFile(fd)
		if err != nil {
			resp.Error = proto.String("File[" + fileName + "][generate]: " + err.Error())
			return resp
		}
		resp.File = append(resp.File, twirpFile)
	}
	return resp
}

func GenerateTwirpFile(fd *descriptor.FileDescriptorProto) (*plugin.CodeGeneratorResponse_File, error) {

	name := fd.GetName()

	vars := templates.TwirpTemplateVariables{
		FileName: name,
	}

	svcs := fd.GetService()
	for _, svc := range svcs {
		svcURL := fmt.Sprintf("%s.%s", fd.GetPackage(), svc.GetName())
		twirpSvc := &templates.TwirpService{
			Name:       svc.GetName(),
			ServiceURL: svcURL,
		}

		for _, method := range svc.GetMethod() {
			inputImport, inputObject := getImportAndObject(method.GetInputType())
			vars.Imports = append(vars.Imports, &templates.TwirpImport{
				From:   inputImport,
				Import: inputObject,
			})

			outputImport, outputObject := getImportAndObject(method.GetOutputType())
			vars.Imports = append(vars.Imports, &templates.TwirpImport{
				From:   outputImport,
				Import: outputObject,
			})

			twirpMethod := &templates.TwirpMethod{
				ServiceURL:  svcURL,
				ServiceName: twirpSvc.Name,
				Name:        method.GetName(),
				Input:       inputObject,
				Output:      outputObject,
			}

			twirpSvc.Methods = append(twirpSvc.Methods, twirpMethod)
		}
		vars.Services = append(vars.Services, twirpSvc)
	}

	var buf = &bytes.Buffer{}
	err := templates.TwirpTemplate.Execute(buf, vars)
	if err != nil {
		return nil, err
	}

	resp := &plugin.CodeGeneratorResponse_File{
		Name:    proto.String(strings.TrimSuffix(name, path.Ext(name)) + "_twirp.py"),
		Content: proto.String(buf.String()),
	}

	return resp, nil
}

func getImportAndObject(name string) (string, string) {
	name = strings.TrimPrefix(name, ".")
	paths := strings.Split(name, ".")
	importPath := "." + strings.Join(paths[:len(paths)-1], ".") + "_pb2"
	return importPath, paths[len(paths)-1]
}

func getFileDescriptor(files []*descriptor.FileDescriptorProto, name string) (*descriptor.FileDescriptorProto, error) {
	//Assumption: Number of files will not be large enough to justify making a map
	for _, f := range files {
		if f.GetName() == name {
			return f, nil
		}
	}
	return nil, errors.New("Could not find descriptor")
}
