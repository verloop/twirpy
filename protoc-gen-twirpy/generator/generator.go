package generator

import (
	"bytes"
	"errors"
	"fmt"
	"path"
	"strings"

	"github.com/golang/protobuf/protoc-gen-go/descriptor"
	plugin "github.com/golang/protobuf/protoc-gen-go/plugin"
	"google.golang.org/protobuf/proto"
)

func Generate(r *plugin.CodeGeneratorRequest) *plugin.CodeGeneratorResponse {
	resp := &plugin.CodeGeneratorResponse{}
	resp.SupportedFeatures = proto.Uint64(uint64(plugin.CodeGeneratorResponse_FEATURE_PROTO3_OPTIONAL))

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

	vars := TwirpTemplateVariables{
		FileName: name,
	}

	svcs := fd.GetService()
	for _, svc := range svcs {
		svcURL := fmt.Sprintf("%s.%s", fd.GetPackage(), svc.GetName())
		twirpSvc := &TwirpService{
			Name:       svc.GetName(),
			ServiceURL: svcURL,
		}

		for _, method := range svc.GetMethod() {
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

	resp := &plugin.CodeGeneratorResponse_File{
		Name:    proto.String(strings.TrimSuffix(name, path.Ext(name)) + "_twirp.py"),
		Content: proto.String(buf.String()),
	}

	return resp, nil
}

func getSymbol(name string) string {
	return strings.TrimPrefix(name, ".")
}

func getFileDescriptor(files []*descriptor.FileDescriptorProto, name string) (*descriptor.FileDescriptorProto, error) {
	//Assumption: Number of files will not be large enough to justify making a map
	for _, f := range files {
		if f.GetName() == name {
			return f, nil
		}
	}
	return nil, errors.New("could not find descriptor")
}
