fso = new ActiveXObject("Scripting.FileSystemObject");

function convertHeaderFile(filename) {
  inFile = fso.OpenTextFile(filename, 1);
  outFile = fso.CreateTextFile(filename+".out");
  inFunc = false;
  while(!inFile.AtEndOfStream) {
    line = inFile.ReadLine();
    if(line.substr(0, 11) == "LIBSSH2_API") {
      outFile.WriteLine("#ifdef staticlinking");
      inFunc = true;
    }
    outFile.WriteLine(line);
    if(inFunc && line.match(/;/)) {
      outFile.WriteLine("#endif");
      inFunc = false;
    }
  }
  inFile.close();
  outFile.close();
}

convertHeaderFile("libssh2.h");
convertHeaderFile("libssh2_sftp.h");
