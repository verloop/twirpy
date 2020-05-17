package main

import (
	"io/ioutil"
	"log"
	"os"

	"github.com/golang/protobuf/proto"
	plugin "github.com/golang/protobuf/protoc-gen-go/plugin"
	"github.com/verloop/twirpy/protoc-gen-twirpy/generator"
)

func main() {
	data, err := ioutil.ReadAll(os.Stdin)
	if err != nil {
		log.Fatalln("could not read from stdin", err)
		return
	}
	var req = &plugin.CodeGeneratorRequest{}
	err = proto.Unmarshal(data, req)
	if err != nil {
		log.Fatalln("could not unmarshal proto", err)
		return
	}
	if len(req.GetFileToGenerate()) == 0 {
		log.Fatalln("no files to generate")
		return
	}
	resp := generator.Generate(req)

	if resp == nil {
		resp = &plugin.CodeGeneratorResponse{}
	}

	data, err = proto.Marshal(resp)
	if err != nil {
		log.Fatalln("could not unmarshal response proto", err)
	}
	_, err = os.Stdout.Write(data)
	if err != nil {
		log.Fatalln("could not write response to stdout", err)
	}
}
