# pyKeysend: send large amounts of data using lightning keysend payments #


## Overview ##

Keysend payments have a limited amount of data that can be attached to them. This module stemed out of a desire to transfer large amounts of data over lightning keysend payments. The thought was that a protocol could be developed to create a TCP like socket running over data attached to keysend payments. This could allow data to be privately transferred in exchange for payments, and allow parties to communicate regardless of how they are connected to the lightning network (whether they have a public dedicated static IP address or an open firewall).


So far, this module is in an alpha level state and only a simple data transfer mechanism has been developed and is being used to further assess the feasibility of such a socket connection. This module uses the LND grpc interface to send and receive data over keysend messages. The module breaks apart the data to be transferred into many smaller chunks and sends it using many keysend payments. The receiver then takes all payments and their attached data and reassembles it into the original message.


### Current limitations: ###

- The receiver needs to be started before the sender begings sending.
- The receiver can't receive any more keysend payments with the same TLV record key from anyone else at the same time and the receiver can only receive one message from the sender at a time.
- If one of the sender's payments fails, the entire process fails.




In general, the transfer rate is __very slow__. It's unclear what the bottleneck is in the process, the CPU on the nodes tested with is not highly loaded while sending or receiving data. There may be some rate limiting on LND. With that being said, this entire concept may have no practical use for a variety of reasons, but it is an interesting exploratory excersise.



### Things needed to extend this to a socket: ###

- Some kind of notion of a socket's port and socket identifier
- A connection open and close message
- A connection timeout setting and keepalive message.
- Some way to get return messages back to the initiator of the connection without revealing their nodes pubkey.
- Define a custom TLV record key (and place it here: https://github.com/satoshisstream/satoshis.stream/blob/main/TLV_registry.md).
- ?






## Example ##

First, place `admin.macaroon` and `tls.cert` in a subdirectory of your current working directory named `config`, then:

### Receiver ###

Input

```python
from keysend import keysend
next(keysend(LNDhost='YourHostName:10009').ReceiveMessages())

```

~ *Wait and hope no other keysends are sent at the same time !* ~

Output
```
bytes to transfer: 184302

---------------------------------------------------------------------------
new chunk
percent complete: 0.43407016744256716

---------------------------------------------------------------------------
new chunk
percent complete: 0.8681403348851343

---------------------------------------------------------------------------
new chunk
percent complete: 1.3022105023277013

---------------------------------------------------------------------------
new chunk
percent complete: 1.7362806697702686

---------------------------------------------------------------------------
new chunk
percent complete: 2.1703508372128355

---------------------------------------------------------------------------
new chunk
percent complete: 2.6044210046554026

---------------------------------------------------------------------------
new chunk
percent complete: 3.0384911720979697

---------------------------------------------------------------------------
new chunk
percent complete: 3.4725613395405373

---------------------------------------------------------------------------
new chunk
percent complete: 3.906631506983104

---------------------------------------------------------------------------
new chunk
percent complete: 4.340701674425671

---------------------------------------------------------------------------
new chunk
percent complete: 4.7747718418682386

---------------------------------------------------------------------------
new chunk
percent complete: 5.208842009310805





... ... ... ... ... ... ... ... ... ... ... ...

~ skipping some boring messages ! ~

... ... ... ... ... ... ... ... ... ... ... ...






---------------------------------------------------------------------------
new chunk
percent complete: 95.0613666699222

---------------------------------------------------------------------------
new chunk
percent complete: 95.49543683736475

---------------------------------------------------------------------------
new chunk
percent complete: 95.92950700480732

---------------------------------------------------------------------------
new chunk
percent complete: 96.36357717224989

---------------------------------------------------------------------------
new chunk
percent complete: 96.79764733969246

---------------------------------------------------------------------------
new chunk
percent complete: 97.23171750713503

---------------------------------------------------------------------------
new chunk
percent complete: 97.6657876745776

---------------------------------------------------------------------------
new chunk
percent complete: 98.09985784202017

---------------------------------------------------------------------------
new chunk
percent complete: 98.53392800946274

---------------------------------------------------------------------------
new chunk
percent complete: 98.9679981769053

---------------------------------------------------------------------------
new chunk
percent complete: 99.40206834434787

---------------------------------------------------------------------------
new chunk
percent complete: 99.83613851179042

---------------------------------------------------------------------------
new chunk
percent complete: 100.0


transfer complete

sha256 hash of the data sent: b1674191a88ec5cdd733e4240a81803105dc412d6c6708d53ab94fc248f4f553
total chunks:      231
bytes transferred: 184302 bytes

waiting for new message
```


### Sender ###

Input

```python
from keysend import keysend
keysend(LNDhost='YourHostName:10009').SendMessage(keysend_message=open('bitcoin.pdf', 'rb').read(),target_pubkey='PubKeyToSendTo')

```


Output

```
bytes to transfer: 184302

---------------------------------------------------------------------------
chunk sent
payment:          1 sat
fee:              0 sat
percent complete: 0.43407016744256716

---------------------------------------------------------------------------
chunk sent
payment:          1 sat
fee:              0 sat
percent complete: 0.8681403348851343

---------------------------------------------------------------------------
chunk sent
payment:          1 sat
fee:              0 sat
percent complete: 1.3022105023277013

---------------------------------------------------------------------------
chunk sent
payment:          1 sat
fee:              0 sat
percent complete: 1.7362806697702686

---------------------------------------------------------------------------
chunk sent
payment:          1 sat
fee:              0 sat
percent complete: 2.1703508372128355

---------------------------------------------------------------------------
chunk sent
payment:          1 sat
fee:              0 sat
percent complete: 2.6044210046554026

---------------------------------------------------------------------------
chunk sent
payment:          1 sat
fee:              0 sat
percent complete: 3.0384911720979697

---------------------------------------------------------------------------
chunk sent
payment:          1 sat
fee:              0 sat
percent complete: 3.4725613395405373

---------------------------------------------------------------------------
chunk sent
payment:          1 sat
fee:              0 sat
percent complete: 3.906631506983104

---------------------------------------------------------------------------
chunk sent
payment:          1 sat
fee:              0 sat
percent complete: 4.340701674425671

---------------------------------------------------------------------------
chunk sent
payment:          1 sat
fee:              0 sat
percent complete: 4.7747718418682386

---------------------------------------------------------------------------
chunk sent
payment:          1 sat
fee:              0 sat
percent complete: 5.208842009310805




... ... ... ... ... ... ... ... ... ... ... ...

~ skipping some boring messages ! ~

... ... ... ... ... ... ... ... ... ... ... ...




---------------------------------------------------------------------------
chunk sent
payment:          1 sat
fee:              0 sat
percent complete: 95.0613666699222

---------------------------------------------------------------------------
chunk sent
payment:          1 sat
fee:              0 sat
percent complete: 95.49543683736475

---------------------------------------------------------------------------
chunk sent
payment:          1 sat
fee:              0 sat
percent complete: 95.92950700480732

---------------------------------------------------------------------------
chunk sent
payment:          1 sat
fee:              0 sat
percent complete: 96.36357717224989

---------------------------------------------------------------------------
chunk sent
payment:          1 sat
fee:              0 sat
percent complete: 96.79764733969246

---------------------------------------------------------------------------
chunk sent
payment:          1 sat
fee:              0 sat
percent complete: 97.23171750713503

---------------------------------------------------------------------------
chunk sent
payment:          1 sat
fee:              0 sat
percent complete: 97.6657876745776

---------------------------------------------------------------------------
chunk sent
payment:          1 sat
fee:              0 sat
percent complete: 98.09985784202017

---------------------------------------------------------------------------
chunk sent
payment:          1 sat
fee:              0 sat
percent complete: 98.53392800946274

---------------------------------------------------------------------------
chunk sent
payment:          1 sat
fee:              0 sat
percent complete: 98.9679981769053

---------------------------------------------------------------------------
chunk sent
payment:          1 sat
fee:              0 sat
percent complete: 99.40206834434787

---------------------------------------------------------------------------
chunk sent
payment:          1 sat
fee:              0 sat
percent complete: 99.83613851179042

---------------------------------------------------------------------------
chunk sent
payment:          1 sat
fee:              0 sat
percent complete: 100.0


sha256 hash of the data sent: b1674191a88ec5cdd733e4240a81803105dc412d6c6708d53ab94fc248f4f553
total chunks:      231
transfer rate:     400.14488053856684 bytes/second
bytes transferred: 184302 bytes
total fees:        0 sat
total payments:    231 sat
total cost:        231 sat
fee rate:          1.2533776084904125 sat/(1000 byte)
```

In the above example, a transfer rate of 400 bytes/second was achieved. At one point, 2,800 bytes/second was achieved, but it is unclear what network conditions resulted in that higher transfer rate.



## Copyright ##

Copyright (c) 2023, [Andy Schroder](http://AndySchroder.com)

## License ##

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT, OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

  
  
________________________________________________________________














