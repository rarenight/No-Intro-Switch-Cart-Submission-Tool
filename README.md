To-do:
- TESTING
- Add multi-title cart support
- Auto-format No-Intro titles
- Further polish, like a progress window for hash calculation
- Integrate NX Game Info (and possibly other submodules like hactoolnet) directly into the script to eliminate manual copy and pasting
- Compile into a user-friendly EXE

Readme:

So, you want to submit a Switch cart to No-Intro? I developed a quick and easy Python script which standardizes forum submissions into easily-imported XML files.

**NOTE NOTE NOTE this is in EARLY ALPHA and has been MINIMALLY TESTED so it may BREAK at any time for any reason, use at your own risk and double check its output!**

You'll need Python with the PyQt5 dependency installed (`pip install pyqt5`) along with [NX Game Info](https://github.com/garoxas/NX_Game_Info) (and the appropriate prod.keys) before you get started.

First, open the program and click "Import NX Game Info". In the window that pops up, paste the output that NX Game Info provides you and press Import:

![1 nx game info output](https://github.com/user-attachments/assets/e4c83e0c-0cd5-47f7-bea0-d1a4f91dccbe)

You'll (hopefully) see the Game Name, Languages, and GameID1 auto-populated. It should also populate the version and update in File Info. If for whatever reason NXGameInfo messes up, you can always manually type the values.
DOES NOT SUPPORT MULTI-TITLE CARTS YET.

Add the applicable cart region so all fields are filled out:

![image](https://github.com/user-attachments/assets/98b2f17d-44e4-4589-86b9-43401e9d5ca8)

Then click the "Dump Info", fill out the Dumper and Tool fields, and click "Generate Card ID Values". Drag and drop the (Card ID) binary file that nxdumptool outputs into the window and the Card ID values should (hopefully) populate like this:

![image](https://github.com/user-attachments/assets/e447a6b8-2990-4201-b608-b9d72427db26)

A custom dump date can be specified if your cart wasn't dumped the same day.

Then click the "Media Info" tab and fill out all the values manually. A dropdown menu allows you to select a downwards triangle for your convenience.

![image](https://github.com/user-attachments/assets/4626e057-effb-482c-ac26-f00bd4869e5a)

Click the File Info tab and then "Import Hashes." If you don't already have a Full XCI, click "Generate Full XCI" to build one.

Drag and drop the Default XCI, then (Initial Area) BIN file, then the Full XCI file into the window and their hashes will auto-populate. Please note this takes a while for large files, please be patient.

![image](https://github.com/user-attachments/assets/6ee348b2-9d1e-4c9c-91bb-2cd7a01b63dd)

When all fields are populated as shown in the above image, click "Generate Submission" and an XML file will be generated in your chosen directory.

This program generates an XML output file that looks like this:

![image](https://github.com/user-attachments/assets/6ba5ca81-21ae-453f-a038-6c76ca7620f4)

They can then be easily imported into No-Intro's backend in a standardized and uniform format:

![image](https://github.com/user-attachments/assets/6fccc898-132a-4b50-81e0-5187a5e6edf8)

![image](https://github.com/user-attachments/assets/2fc094fa-6c12-4580-b9ac-3f22d6476cdf)
