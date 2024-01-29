package generator

type TwirpTemplateVariables struct {
	FileName string
	Imports  []*TwirpImport
	Services []*TwirpService
}

type TwirpService struct {
	ServiceURL string
	Name       string
	Comment    string
	Methods    []*TwirpMethod
}

type TwirpMethod struct {
	ServiceURL      string
	ServiceName     string
	Name            string
	Comment         string
	Input           string
	Output          string
	QualifiedInput  string
	QualifiedOutput string
}

type TwirpImport struct {
	From   string
	Import string
	Alias  string
}
