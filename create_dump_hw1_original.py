import pickle, logging

from memoryfs import *

if __name__ == "__main__":

  # Initialize file for logging
  # Changer logging level to INFO to remove debugging messages
  logging.basicConfig(filename='memoryfs.log', filemode='w', level=logging.DEBUG)

  # Replace with your UUID, encoded as a byte array
  UUID = b'\x12\x34\x56\x78'

  # Initialize file system data
  logging.info('Initializing data structures...')
  RawBlocks = DiskBlocks()
  RawBlocks.InitializeBlocks(True,UUID)

  # Show file system information and contents of first few blocks
  RawBlocks.PrintFSInfo()
  RawBlocks.PrintBlocks("Initialized",0,16)

  # Initialize root inode
  file = FileName(RawBlocks)
  file.InitRootInode()

  i1 = file.Create(0, "data", INODE_TYPE_DIR)
  i2 = file.Create(0, "foo", INODE_TYPE_DIR)
  i3 = file.Create(0, "bar", INODE_TYPE_DIR)
  i4 = file.Create(0, "file1.txt", INODE_TYPE_FILE)
  i5 = file.Create(0, "file2.txt", INODE_TYPE_FILE)
  i6 = file.Create(0, "file3.txt", INODE_TYPE_FILE)
  i7 = file.Create(0, "file4.txt", INODE_TYPE_FILE)
  i8 = file.Create(i1, "file5.txt", INODE_TYPE_FILE)
  i9 = file.Create(i2, "file6.txt", INODE_TYPE_FILE)
  i10 = file.Create(i3, "file7.txt", INODE_TYPE_FILE)
  i11 = file.Create(i3, "file8.txt", INODE_TYPE_FILE)
  i12 = file.Create(i2, "bar", INODE_TYPE_DIR)
  i13 = file.Create(i12, "file9.txt", INODE_TYPE_FILE)

  print ('Lookup (data,0) = ' + str(file.Lookup('data',0)))
  print ('Lookup (foo,0) = ' + str(file.Lookup('foo',0)))
  print ('Lookup (bar,0) = ' + str(file.Lookup('bar',0)))
  print ('Lookup (notexist,0) = ' + str(file.Lookup('notexist',0)))
  print ('Lookup (file1.txt,0) = ' + str(file.Lookup('file1.txt',0)))
  print ('Lookup (file2.txt,0) = ' + str(file.Lookup('file2.txt',0)))
  print ('Lookup (file3.txt,0) = ' + str(file.Lookup('file3.txt',0)))
  print ('Lookup (file4.txt,0) = ' + str(file.Lookup('file4.txt',0)))
  print ('Lookup (file5.txt,i1) = ' + str(file.Lookup('file5.txt',i1)))
  print ('Lookup (file6.txt,i2) = ' + str(file.Lookup('file6.txt',i2)))
  print ('Lookup (file7.txt,i3) = ' + str(file.Lookup('file7.txt',i3)))
  print ('Lookup (file8.txt,i3) = ' + str(file.Lookup('file8.txt',i3)))
  print ('Lookup (bar,i2) = ' + str(file.Lookup('bar',i2)))
  print ('Lookup (file9.txt,i3) = ' + str(file.Lookup('file9.txt',i12)))

  f = file.Lookup('file8.txt',i3)
  data = bytearray("Contents of file8.txt.","utf-8")
  offset = file.Write(f, 0, data)
  data2 = bytearray("Adding more content to file8.txt.","utf-8")
  file.Write(f, offset, data2)

  f2 = file.Lookup('file6.txt',i2)
  data3 = bytearray("Contents of file6.txt","utf-8")
  file.Write(f2, 0, data3)

  f3 = file.Lookup('file9.txt',i12)
  data4 = bytearray("Contents of file9.txt","utf-8")
  file.Write(f3, 0, data4)

  f4 = file.Lookup('file1.txt',0)
  data5 = bytearray("BEGIN. Contents of file1.txt - this exceeds a BLOCK_SIZE of 128. Contents of file1.txt - this exceeds a BLOCK_SIZE of 128. Contents of file1.txt - this exceeds a BLOCK_SIZE of 128. Contents of file1.txt - this exceeds a BLOCK_SIZE of 128. END.","utf-8")
  file.Write(f4, 0, data5)

  read1 = file.Read(f4,0,256)
  print ('read1: ' + str(read1))

  RawBlocks.PrintBlocks("End",0,32)
  RawBlocks.DumpToDisk(UUID)



