#!/usr/bin/env python3


###############################################################################
###############################################################################
# Copyright (c) 2023, Andy Schroder
# See the file README.md for licensing information.
###############################################################################
###############################################################################


import codecs, grpc, os

from time import time
from hashlib import sha256
from secrets import token_bytes


# Generate the following modules by compiling with the grpcio-tools.
# See https://github.com/lightningnetwork/lnd/blob/master/docs/grpc/python.md for instructions. note, need to change python commands to use python3 instead of python.
import router_pb2 as routerrpc, router_pb2_grpc as routerstub
import lightning_pb2 as lnrpc, lightning_pb2_grpc as lightningstub




def chunks(data, n):
	for i in range(0, len(data), n):
		yield data[i:i + n]





HeaderSize = 10			#10 should allow 10**10 bytes to be sent.

# note: chunksize needs to be greater than HeaderSize
#chunksize=1154
chunksize=800










class keysend():
	def __init__(self,LNDhost,macaroon_filepath='config/admin.macaroon',cert_filepath='config/tls.cert'):

		self.macaroon = codecs.encode(open(macaroon_filepath, 'rb').read(), 'hex')
		os.environ['GRPC_SSL_CIPHER_SUITES'] = 'HIGH+ECDSA'
		cert = open(cert_filepath, 'rb').read()
		ssl_creds = grpc.ssl_channel_credentials(cert)
		auth_creds = grpc.metadata_call_credentials(self.metadata_callback)
		combined_creds = grpc.composite_channel_credentials(ssl_creds, auth_creds)

		self.channel = grpc.secure_channel(LNDhost, combined_creds)




	def metadata_callback(self,context, callback):
		callback([('macaroon', self.macaroon)], None)




	def SendMessage(self,keysend_message,target_pubkey):

		stub = routerstub.RouterStub(self.channel)


		if type(keysend_message) is str:
			MessageBytes=keysend_message.encode()		#convert to binary
		else:	#assume it is already binary
			MessageBytes=keysend_message

		TheMessageToSend = f"{len(MessageBytes):<{HeaderSize}}".encode()+MessageBytes		# indicate the number of bytes in the message in a header before the message
		TotalBytesToTransfer=len(TheMessageToSend)

		print()
		print()
		print("bytes to transfer: "+str(TotalBytesToTransfer))

		StartTime=time()

		THEpayment=1
		TotalChunks=0
		TotalFees=0
		BytesTransferred=0

		for chunk in chunks(TheMessageToSend,chunksize):

			preimage=token_bytes(32)
			phash=sha256(preimage).digest()

			dest_custom_records = {
						#don't think  this uses amp, but keysend. not sure how to do amp, but don't think will ever pay more than 1 sat so should never even need it anyway.
						5482373484: preimage,

						# Custom data encapsulating record
						34349334: chunk
						}

			request = routerrpc.SendPaymentRequest(
									payment_hash = phash,
									amt = THEpayment,
									dest = bytes.fromhex(target_pubkey),
									dest_custom_records = dest_custom_records,
									timeout_seconds = 2,
									allow_self_payment = True,
									no_inflight_updates = True,
								)

			for response in stub.SendPaymentV2(request):
				if response.status==2:

					CurrentFee=response.fee
					TotalFees+=CurrentFee
					TotalChunks+=1
					BytesTransferred+=len(chunk)

					print()
					print('---------------------------------------------------------------------------')
					print('chunk sent')
					print('payment:          '+str(THEpayment)+' sat')
					print('fee:              '+str(CurrentFee)+' sat')
					print('percent complete: '+str(BytesTransferred/TotalBytesToTransfer*100))





		TotalTime=time()-StartTime
		TotalPayments=TotalChunks*THEpayment
		TotalCost=TotalPayments+TotalFees

		print()
		print()
		print("sha256 hash of the data sent: "+sha256(MessageBytes).hexdigest())
		print("total chunks:      "+str(TotalChunks))
		print("transfer rate:     "+str(len(TheMessageToSend)/TotalTime)+' bytes/second')
		print("bytes transferred: "+str(TotalBytesToTransfer)+' bytes')
		print("total fees:        "+str(TotalFees)+' sat')
		print("total payments:    "+str(TotalPayments)+' sat')
		print("total cost:        "+str(TotalCost)+' sat')
		print("fee rate:          "+str(TotalCost*1000/TotalBytesToTransfer)+' sat/(1000 byte)')
		print()
		print()










	def ReceiveMessages(self):
		"""Receive multiple data chunks and put them together to form a message.
		HeaderSize indicates the amount of bytes at the beginning that are used
		to define the entire message length.
		"""

		stub = lightningstub.LightningStub(self.channel)
		request = lnrpc.InvoiceSubscription()


		NewMessage = True

		for response in stub.SubscribeInvoices(request):
			if response.state==1:							# must be SETTLED and not OPEN, CANCELED, or ACCEPTED

				data=response.htlcs[0].custom_records[34349334]			# get the data that was sent over the keysend payment

				if NewMessage:
					TotalBytesToTransfer = int(data[:HeaderSize])
					Message = bytes()
					NewMessage = False
					TotalChunks=0

					print()
					print()
					print("bytes to transfer: "+str(TotalBytesToTransfer+HeaderSize))

				print()
				print('---------------------------------------------------------------------------')
				print('new chunk')

				Message += data
				TotalChunks+=1

				BytesTransferred=len(Message)
				print('percent complete: '+str(BytesTransferred/(TotalBytesToTransfer+HeaderSize)*100))

				if len(Message)-HeaderSize == TotalBytesToTransfer:	#receive data until a complete message is reconstructed, then wait for a new message
					NewMessage = True

					print()
					print()
					print('transfer complete')
					print()
					print("sha256 hash of the data sent: "+sha256(Message[HeaderSize:]).hexdigest())
					print("total chunks:      "+str(TotalChunks))
					print("bytes transferred: "+str(TotalBytesToTransfer+HeaderSize)+' bytes')
					print()
					print('waiting for new message')
					print()
					print()

					yield Message[HeaderSize:]












