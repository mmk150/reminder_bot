{ buildPythonPackage
, poetry-core
, discordpy
, dateutils
}:

buildPythonPackage {
  pname = "thoth";
  version = "unstable";

  format = "pyproject";

  src = ./..;
  propagatedBuildInputs = [
    poetry-core
    discordpy
    dateutils
  ];

  # No tests are available
  doCheck = false;
  pythonImportsCheck = [
    "thoth"
  ];
}
