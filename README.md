# Ouroboros
Code that writes code.

Setup your API key in a "key.txt" file and modify the remote_agent file to reflect the location of your key.

By default, this code uses GPT-3.5 but you can use GPT-4 by changing the remote_agent file.

Put the product that you want to build in the "product" field of the config file in config/.

Then run the program by running product_manager.py.

The project assumes your python version is called as "python3" from the shell. If not, edit the developer file to reflect how python is called on yoru system.

It works most of the time. Is a product retries count that you can set in config, which will restart the whole process n times. There is also a developer retries count feature, which you set in the same place, and which will just retry a particular code step m times.

Sometimes you do have to do it multiple times, it prints out the initial instructions and the code that is being delivered to help with debugging.

Feel free to offer improvements!
