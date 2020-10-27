import pickle, logging, string

from memoryfs import *

## This class implements an interactive shell to navigate the file system

class FSShell():
  def __init__(self, file):
    # cwd stored the inode of the current working directory
    # we start in the root directory
    self.cwd = 0
    self.FileObject = file

  # implements cd (change directory)
  def cd(self, dir):
    i = self.FileObject.Lookup(dir,self.cwd)
    if i == -1:
      print ("Error: not found\n")
      return -1
    inobj = InodeNumber(self.FileObject.RawBlocks,i)
    inobj.InodeNumberToInode()
    if inobj.inode.type != INODE_TYPE_DIR:
      print ("Error: not a directory\n")
      return -1
    self.cwd = i

  # implements ls (lists files in directory)
  def ls(self):
      Inodes = Inode()
      block_0 = self.FileObject.RawBlocks.Get(4)
      block_1 = self.FileObject.RawBlocks.Get(5)
      i = self.cwd
      if (i < 8):
          Inodes.InodeFromBytearray(block_0[(i*16):(i*16+15)])
      else:
          Inodes.InodeFromBytearray(block_1[((i-8)*16):((i-8)*16+15)])
      block = self.FileObject.RawBlocks.Get(Inodes.block_numbers[0])
      index = 0
      while (1<2):
          Filename = self.FileObject.HelperGetFilenameString(block, index).decode()
          print(Filename)
          if (Filename == ""):
              break
          index+=1

  # implements cat (print file contents)
  def cat(self, filename):
      i = self.cwd
      inode_Filename = self.FileObject.Lookup(filename,i)
      if inode_Filename == -1:
          print ("File not found\n")
          return -1
      Inodes = Inode()
      block_0 = self.FileObject.RawBlocks.Get(4)
      block_1 = self.FileObject.RawBlocks.Get(5)
      if (inode_Filename < 8):
          Inodes.InodeFromBytearray(block_0[(inode_Filename*16):(inode_Filename*16+15)])
      else:
          Inodes.InodeFromBytearray(block_1[((inode_Filename-8)*16):((inode_Filename-8)*16+15)])
      file_data = self.FileObject.Read(inode_Filename, 0, Inodes.size)
      print(file_data)


  def Interpreter(self):
    while (True):
      command = input("[cwd=" + str(self.cwd) + "]:")
      splitcmd = command.split()
      if splitcmd[0] == "cd":
        if len(splitcmd) != 2:
          print ("Error: cd requires one argument")
        else:
          self.cd(splitcmd[1])
      elif splitcmd[0] == "cat":
        if len(splitcmd) != 2:
          print ("Error: cat requires one argument")
        else:
          self.cat(splitcmd[1])
      elif splitcmd[0] == "ls":
        self.ls()
      elif splitcmd[0] == "exit":
        return
      else:
        print ("command " + splitcmd[0] + "not valid.\n")


if __name__ == "__main__":

  # Initialize file for logging
  # Changer logging level to INFO to remove debugging messages
  logging.basicConfig(filename='memoryfs.log', filemode='w', level=logging.DEBUG)

  # Replace with your UUID, encoded as a byte array
  UUID = b'\x12\x34\x56\x78'

  # Initialize file system data
  logging.info('Initializing data structures...')
  RawBlocks = DiskBlocks()
  # Load blocks from dump file
  RawBlocks.InitializeBlocks(False,UUID)

  # Show file system information and contents of first few blocks
  RawBlocks.PrintFSInfo()
  RawBlocks.PrintBlocks("Initialized",0,16)

  # Initialize FileObject inode
  FileObject = FileName(RawBlocks)

  # -------Added by Sujan-----
  # Finding Inode blocks
  block_0 = RawBlocks.Get(4)
  block_1 = RawBlocks.Get(5)

  Inodes = Inode()
  # Printing 16 Inode objects
  for i in range(8):
      logging.info(block_0[(i*16):(i*16+15)])
      Inodes.InodeFromBytearray(block_0[(i*16):(i*16+15)])
      Inodes.Print()
  for i in range(8):
      logging.info(block_1[(i*16):(i*16+15)])
      Inodes.InodeFromBytearray(block_1[(i*16):(i*16+15)])
      Inodes.Print()

  # Block 6 through Block 10 are directory block. Block 6 is root directory.
  block_6 = RawBlocks.Get(6)
  block_7 = RawBlocks.Get(7)
  block_8 = RawBlocks.Get(8)
  block_9 = RawBlocks.Get(9)
  block_10 = RawBlocks.Get(10)
  block_13 = RawBlocks.Get(13) # required for file9.txt as this file is saved in block 13

  #Finding file and directory name from Blocks
  Filename = FileObject.HelperGetFilenameString(block_6, 4)
  logging.info(Filename)

  #Finding Inodes for file and directory from Blocks
  inode_Filename_1 = FileObject.HelperGetFilenameInodeNumber(block_6, 4)
  logging.info(inode_Filename_1)

  #Printing the contents of file9.txt
  #logging.info(block_13[0:41].decode())

  #Data = "Added data in file9.txt"
  #file9_data = FileObject.Write(13, 21, Data.encode())
  file9_data = FileObject.Read(4, 0, 200)
  logging.info(file9_data)
  #-------End of Sujan's code-----

  myshell = FSShell(FileObject)
  myshell.Interpreter()
