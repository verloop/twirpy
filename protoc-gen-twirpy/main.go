package main

import (
	"log"

	"github.com/verloop/twirpy/protoc-gen-twirpy/generator"

    "github.com/pseudomuto/protokit"
)

func main() {
    if err := protokit.RunPlugin(new(generator.Plugin)); err != nil {
        log.Fatal(err)
    }
}
