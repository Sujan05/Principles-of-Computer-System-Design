import pickle, logging
import sys      # Added by Sujan for assignment 4

from memoryfs_client import BLOCK_SIZE, TOTAL_NUM_BLOCKS, RSM_LOCKED

from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler

# MD5 gives a checksum of 16 byte for one data block
CHECKSUM_SIZE = 16

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
  rpc_paths = ('/RPC2',)

class DiskBlocks():
  def __init__(self):
    # This class stores the raw block array
    self.block = []
    # Initialize raw blocks
    for i in range (0, TOTAL_NUM_BLOCKS):
      putdata = bytearray(BLOCK_SIZE)
      self.block.insert(i,putdata)

    # This class stores the raw checksum array
    self.checksum_array = []
    # Initialize checksum array
    for i in range (0, TOTAL_NUM_BLOCKS):
      putchecksum = bytearray(CHECKSUM_SIZE)
      self.checksum_array.insert(i,putchecksum)


if __name__ == "__main__":

  RawBlocks = DiskBlocks()

  argumentList = sys.argv
  #print(argumentList)
  #print(int(argumentList[1]))
  #print(argumentList[1])
  # Create server
  server = SimpleXMLRPCServer(("localhost", int(argumentList[1])), requestHandler=RequestHandler)

  def Get(block_number):
    result = RawBlocks.block[block_number]
    return result

  server.register_function(Get)

  def Put(block_number, data, checksum):
    RawBlocks.block[block_number] = data
    RawBlocks.checksum_array[block_number] = checksum
    #print(RawBlocks.checksum_array[block_number])
    return 0

  server.register_function(Put)

  def RSM(block_number):
    result = RawBlocks.block[block_number]
    RawBlocks.block[block_number] = RSM_LOCKED
    # RawBlocks.block[block_number] = bytearray(RSM_LOCKED.ljust(BLOCK_SIZE,b'\x01'))
    return result

  server.register_function(RSM)

  # Run the server's main loop
  server.serve_forever()
