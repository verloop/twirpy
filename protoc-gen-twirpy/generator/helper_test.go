package generator

import (
	"testing"

	"github.com/stretchr/testify/require"
)

func TestCamelCase(t *testing.T) {

	for src, res := range map[string]string{
		"_":            "X",
		"__":           "X_",
		"___":          "X__",
		"_1":           "X1",
		"_a":           "XA",
		"_aX":          "XAX",
		"_AX":          "XAX",
		"1AX":          "1AX",
		"AX":           "AX",
		"text":         "Text",
		"text_":        "Text_",
		"text__":       "Text__",
		"text1":        "Text1",
		"text1_":       "Text1_",
		"text1a":       "Text1A",
		"text_a":       "TextA",
		"text_abc":     "TextAbc",
		"text1abc":     "Text1Abc",
		"text_1abc":    "Text_1Abc",
		"text__1abc":   "Text__1Abc",
		"_text1abc":    "XText1Abc",
		"__text1abc":   "XText1Abc",
		"___text1abc":  "X_Text1Abc",
		"__1text1abc":  "X_1Text1Abc",
		"___1text1abc": "X__1Text1Abc",
		"1text1abc":    "1Text1Abc",
		"1_text1abc":   "1Text1Abc",
	} {

		require.Equal(t, res, CamelCase(src), src)
	}
}
