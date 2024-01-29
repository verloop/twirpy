package main

import (
	"io/ioutil"
	"os"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"testing"
)

func loadProto(t *testing.T) *os.File {
	file, err := os.Open("test_data/protoc_input.data")
	require.NoError(t, err)
	return file
}

func loadGenerated(t *testing.T) []byte {
	file, err := os.Open("test_data/protoc_output.data")
	require.NoError(t, err)
	result, err := ioutil.ReadAll(file)
	require.NoError(t, err)
	return result
}

func captureOutput(t *testing.T, f func()) []byte {
	orig := os.Stdout
	r, w, err := os.Pipe()
	require.NoError(t, err)
	os.Stdout = w
	f()
	os.Stdout = orig
	w.Close()
	out, err := ioutil.ReadAll(r)
	require.NoError(t, err)
	return out
}

func TestMain(t *testing.T) {
	os.Stdin = loadProto(t)
	result := captureOutput(t, main)
	assert.Equal(t, string(loadGenerated(t)), string(result))
}
