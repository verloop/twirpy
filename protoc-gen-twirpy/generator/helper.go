package generator

import (
	"bytes"
	"io"
	"strings"
	"unicode"
)

// An alternative of the function 'CamelCase' in a private package:
// https://github.com/twitchtv/twirp/blob/master/internal/gen/stringutils/stringutils.go
func CamelCase(s string) string {

	const Delemeter = '_'

	writer := bytes.NewBuffer(make([]byte, 0, len(s)))
	reader := strings.NewReader(s)

	var prev rune
	for {
		r, _, err := reader.ReadRune()
		if err == io.EOF {
			break
		}

		if prev == 0x00 && r == Delemeter {
			writer.WriteRune('X')

		} else if unicode.IsLower(r) && (prev == 0x00 || prev == Delemeter || (prev >= '0' && prev <= '9')) {
			if lastIndex := writer.Len() - 1; lastIndex >= 0 && writer.Bytes()[lastIndex] == Delemeter {
				writer.Truncate(lastIndex) // remove delemeter before symbol
			}
			writer.WriteRune(unicode.ToUpper(r))

		} else {
			writer.WriteRune(r)

		}

		prev = r
	}

	return writer.String()
}
