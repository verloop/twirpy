# protoc-gen-twirpy
twirp support for python

# Installing and using plugin
1. Make sure your [GO](https://golang.org/) environment, [Protobuf](https://github.com/protocolbuffers/protobuf) compiler is properly setup.
2. Get dependencies : `go get .`
3. Install the plugin : `go install`  
This will build the plugin and will be available at `$GOBIN` directory which is usually `$GOPATH/bin`
4. Generate code for `haberdasher.proto` using twirpy plugin :  
`protoc --plugin=protoc-gen-twirpy --python_out=./ --twirpy_out=./ haberdasher.proto`  
  - plugin : It tells protoc which all plugins to use
  - python_out : The directory where generated Protobuf Python code needs to be saved.
  - twirpy_out : The directory where generated Twirp Python server and client code needs to be saved.

The compiler gives the error below if it's not able to find the plugin.
```
Please specify a program using absolute path or make sure the program is available in your PATH system variable
--twirpy_out: protoc-gen-twirpy: Plugin failed with status code 1.
```
In such cases, you can give absolute path to plugin, eg : `--plugin=protoc-gen-twirpy=$GOBIN/protoc-gen-twirpy`
