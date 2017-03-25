# ~~whisper

Whisper is a one-time-pad based crypto-chat that allows two nodes to anonymously communicate with each other on a network.

## Legal Disclaimer

**It is the end user's responsibility to obey all local, state, and federal laws. The developer assumes no liability for any misuse or damages caused by this software.**

## Usage

```
[sudo] python whisper.py [options]                        
                                                           
  ~~All in One                                             
       --serve        Create a server for GUI interaction  
                                                           
  ~~Main Options                                           
       -d their_addr  IP address I'm communicating with    
       -dp their_port Port I'm communicating over          
       -p PORT        What communication port to use       
       -w FILE        File to load one-time-pads from      
       -s IN_FILTER   De-sanitize all keys with a filter   
       -v             Verbose mode                         
                                                           
  ~~Watching the Chat                                      
       --listen       Listen and log the chat              
                                                           
  ~~Maintaining Security                                   
       -g FILE        Generate keys and write to file      
       -k KEYS        Number of one-time-pads to generate  
       -l LENGTH      Length of each one-time-pad          
                                                           
       -m FILE        Modify a key file that already exists
       -f OUT_FILTER  Sanitize all keys with a filter      
```

## Setup

> Whisper was created using python 2.7.10

Before whisper can be used for remote communication, the two clients in question will first need to agree upon a large set of K keys, each of length L, where L is larger thant the largest message which will ever be exchanged.

Generating a set of such keys can be done simply by typing:

`python whisper.py -g [key_output_filename] -k [number_of_keys] -l [length_of_each_key]`

These keys will then need to be exchanged in such a way that they cannot be intercepted by an intermediary.

Once both of clients have exchanged keys, they will individually want to encrypt their list of keys with another private key (ideally of size K * L) that only they have access to. To encrypt the file of keys, do:

`python whisper.py -m [key_file_to_encrypt] -f [private_key]`

**Note: If a key from this file is ever reused, the messages sent from one client to the other will not fall under the notion of perfect security.**

When in remote communication with each other, each client also needs to know the IP of the other, as well as the port to access each other on. One particular way of exchanging this info is for one client to learn the info of the other when exchanging keys, and then whisper their info to the other client once they have arrived at a remote location.

## GUI Interaction

The GUI implementation of whisper is the easiest to use. Once you have your file of keys generated from the previous steps, and the info of the other client, you're ready to begin chatting. Do:

`sudo python whisper.py -w [path_to_keys_file] -s [private_key] -d [ip_of_other_client] -dp [port_they_are_listening_on] -p [port_you_want_to_listen_on] --serve`

This sets up a local loopback server for browser interaction on `http://localhost/css`. It additionally sets up a listening socket on the port specified by `-p [port_you_want_to_listen_on]`. This is the port the other client can contact you on.

Open up a browser and go to `http://localhost/css`. On the left banner, you'll need to select the list of keys that you also specified with the terminal option `-w [path_to_keys_file]`. Additionally, if you encrypted your keys with another private key (specified with `-s [private_key]`), you'll need to put that in the sanitization input.

That's it! The textarea provided allows you to send messages by hitting return, and new ones will be automatically received.

## Terminal Interaction

The terminal-only implementation of whisper allows one to avoid setting up a server on localhost:80. You will need two terminal windows: one for listening and logging messages, and one for sending messages.

In the first terminal window, do:

`python whisper.py -w [path_to_keys_file] -s [private_key] -p [port_you_want_to_listen_on] --listen`

This sets up a chat logger, where `-w [path_to_keys_file]` specifies the keys file you generated earlier, `-s [private_key]` specifies the private key you encrypted that file with (if you didn't encrypt it, you can leave this option out), and `-p [port_you_want_to_listen_on]` specifies the port you're listening for messages on.

Next, we want to set up a terminal to send messages. To do that, run

`python whisper.py -w [path_to_keys_file] -s [private_key] -d [ip_of_other_client] -dp [port_they_are_listening_on]`

Where `-w [path_to_keys_file]` specifies the keys file, `-s [private_key]` specifies the private key, `-d [ip_of_other_client]` presumably specifies the IP of the other client, and `-dp [port_they_are_listening_on]` is the port they are listening for messages on.

And you're all set up! If you're having trouble, use `-v` to see if there are connection hangs or `sudo kill -9` the python process if you get an `address already in use` socket error.

## Release Notes

a.3

* First publically available alpha
* Terminal interaction
* GUI interaction, local reverberation of sent and received messages
