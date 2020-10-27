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
  #def ls(self):
#      Inodes = Inode()
#      block_0 = self.FileObject.RawBlocks.Get(4)
#      block_1 = self.FileObject.RawBlocks.Get(5)
#      i = self.cwd
#      if (i < 8):
#          Inodes.InodeFromBytearray(block_0[(i*16):(i*16+15)])
#      else:
#          Inodes.InodeFromBytearray(block_1[((i-8)*16):((i-8)*16+15)])
#      block = self.FileObject.RawBlocks.Get(Inodes.block_numbers[0])
#      index = 0
#      while (1<2):
#          Filename = self.FileObject.HelperGetFilenameString(block, index).decode()
#          print(Filename)
#          if (Filename == ""):
#              break
#          index+=1

  # implements ls (lists files in directory)
  def ls(self):
    inobj = InodeNumber(self.FileObject.RawBlocks, self.cwd)
    inobj.InodeNumberToInode()
    block_index = 0
    while block_index <= (inobj.inode.size // BLOCK_SIZE):
      block = self.FileObject.RawBlocks.Get(inobj.inode.block_numbers[block_index])
      if block_index == (inobj.inode.size // BLOCK_SIZE):
        end_position = inobj.inode.size % BLOCK_SIZE
      else:
        end_position = BLOCK_SIZE
      current_position = 0
      while current_position < end_position:
        entryname = block[current_position:current_position+MAX_FILENAME]
        entryinode = block[current_position+MAX_FILENAME:current_position+FILE_NAME_DIRENTRY_SIZE]
        entryinodenumber = int.from_bytes(entryinode, byteorder='big')
        inobj2 = InodeNumber(self.FileObject.RawBlocks, entryinodenumber)
        inobj2.InodeNumberToInode()
        if inobj2.inode.type == INODE_TYPE_DIR:
          print ("[" + str(inobj2.inode.refcnt) + "]:" + entryname.decode() + "/")
        else:
          print ("[" + str(inobj2.inode.refcnt) + "]:" + entryname.decode())
        current_position += FILE_NAME_DIRENTRY_SIZE
      block_index += 1
    return 0


  # implements cat (print file contents)
  def cat(self, filename):
      i = self.cwd
      inode_Filename = self.FileObject.Lookup(filename,i)
      if inode_Filename == -1:
          print ("Error: File not found\n")
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

  #implement mkdir
  def mkdir(self, dirname):
      i = self.cwd
      inode_position = self.FileObject.FindAvailableInode()
      if inode_position == -1:
        logging.debug ("Create: no free inode available")
        return -1

      # Obtain dir_inode_number_inode, ensure it is a directory
      dir_inode = InodeNumber(self.FileObject.RawBlocks, i)
      dir_inode.InodeNumberToInode()
      if dir_inode.inode.type != INODE_TYPE_DIR:
        logging.debug ("Create: dir is not a directory")
        return -1

      # Find available slot in directory data block
      fileentry_position = self.FileObject.FindAvailableFileEntry(i)
      if fileentry_position == -1:
        logging.debug ("Create: no entry available for another object")
        return -1

      # Ensure it's not a duplicate - if Lookup returns anything other than -1
      if self.FileObject.Lookup(dirname, i) != -1:
        logging.debug ("Create: name already exists")
        return -1

      # Store inode of new directory
      newdir_inode = InodeNumber(self.FileObject.RawBlocks, inode_position)
      newdir_inode.InodeNumberToInode()
      newdir_inode.inode.type = INODE_TYPE_DIR
      newdir_inode.inode.size = 0
      newdir_inode.inode.refcnt = 1
      # Allocate one data block and set as first entry in block_numbers[]
      newdir_inode.inode.block_numbers[0] = self.FileObject.AllocateDataBlock()
      newdir_inode.StoreInode()

      # Add to directory (filename,inode) table
      self.FileObject.InsertFilenameInodeNumber(dir_inode, dirname, inode_position)

      # Add "." to new directory
      self.FileObject.InsertFilenameInodeNumber(newdir_inode, ".", inode_position)

      # Add ".." to new directory
      self.FileObject.InsertFilenameInodeNumber(newdir_inode, "..", i)

      # Update directory inode
      # increment refcnt
      dir_inode.inode.refcnt += 1
      dir_inode.StoreInode()

  #implement create FileName
  def create(self, filename):
      i = self.cwd
      inode_position = self.FileObject.FindAvailableInode()
      if inode_position == -1:
        logging.debug ("Create: no free inode available")
        return -1

      # Obtain dir_inode_number_inode, ensure it is a directory
      dir_inode = InodeNumber(self.FileObject.RawBlocks, i)
      dir_inode.InodeNumberToInode()
      if dir_inode.inode.type != INODE_TYPE_DIR:
        logging.debug ("Create: dir is not a directory")
        return -1

      # Find available slot in directory data block
      fileentry_position = self.FileObject.FindAvailableFileEntry(i)
      if fileentry_position == -1:
        logging.debug ("Create: no entry available for another object")
        return -1

      # Ensure it's not a duplicate - if Lookup returns anything other than -1
      if self.FileObject.Lookup(filename, i) != -1:
        logging.debug ("Create: name already exists")
        return -1

      newfile_inode = InodeNumber(self.FileObject.RawBlocks, inode_position)
      newfile_inode.InodeNumberToInode()
      newfile_inode.inode.type = INODE_TYPE_FILE
      newfile_inode.inode.size = 0
      newfile_inode.inode.refcnt = 1
      # New files are not allocated any blocks; these are allocated on a Write()
      newfile_inode.StoreInode()

      # Add to parent's (filename,inode) table
      self.FileObject.InsertFilenameInodeNumber(dir_inode, filename, inode_position)

      # Update directory inode
      # refcnt incremented by one
      dir_inode.inode.refcnt += 1
      dir_inode.StoreInode()

  def append(self, filename, string):
      i = self.cwd
      inode_Filename = self.FileObject.Lookup(filename,i)
      if inode_Filename == -1:
          print ("Error: File not found\n")
          return -1
      Inodes = Inode()
      block_0 = self.FileObject.RawBlocks.Get(4)
      block_1 = self.FileObject.RawBlocks.Get(5)
      if (inode_Filename < 8):
          Inodes.InodeFromBytearray(block_0[(inode_Filename*16):(inode_Filename*16+15)])
      else:
          Inodes.InodeFromBytearray(block_1[((inode_Filename-8)*16):((inode_Filename-8)*16+15)])
      if (len(string.encode()) > MAX_FILE_SIZE):
          print("Error: String size is larger than the file size\n")
      else:
          bytes_written = self.FileObject.Write(inode_Filename, Inodes.size, string.encode())
          logging.debug("Bytes written: " + str(bytes_written))
      return 0

  def ln(self, target, linkname):
      i = self.cwd
      self.FileObject.Link(target, linkname, i)

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
      elif splitcmd[0] == "mkdir":
          if len(splitcmd) != 2:
            print ("Error: mkdir requires one argument")
          else:
            self.mkdir(splitcmd[1])
      elif splitcmd[0] == "create":
          if len(splitcmd) != 2:
            print ("Error: create requires one argument")
          else:
            self.create(splitcmd[1])
      elif splitcmd[0] == "append":
          if len(splitcmd) != 3:
            print ("Error: append requires two arguments")
          else:
            self.append(splitcmd[1], splitcmd[2])
      elif splitcmd[0] == "ln":
          if len(splitcmd) != 3:
            print ("Error: ln requires two arguments")
          else:
            self.ln(splitcmd[1], splitcmd[2])
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

  #pathname = "data/file5.txt"
  #print(pathname)
  #inode_number = FileObject.GeneralPathToInodeNumber(pathname, 0)
  #inode_number = FileObject.GeneralPathToInodeNumber(pathname, 0)
  #print(inode_number)
  #FileObject.Link(pathname, "sujan", 0)
  #-------End of Sujan's code-----

  myshell = FSShell(FileObject)
  myshell.Interpreter()
