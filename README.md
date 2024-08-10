# Versions

v1.8 - 2024-08-10
- (v1.8) Embedded nxgameinfo_cli executable into the script, (v1.8) Added a "Truncate FullXCI File" button that reverts a Full XCI back to a Default XCI and an Initial Area, (v1.8) Added additional failsafes to prevent Default XCIs / Full XCIs from being mistakenly processed, (v1.7) Added a dropdown for regions, (v1.7) Fixed GameID2 four-digit bug, (v1.7) Add revision auto-fill, (v1.7) Added loose cart toggle, (v1.6) Fixed NX Info import glitch where CLI importing wouldn't detect v0, (v1.6) Added directory selection support for Mac + Linux, (v1.5) Added the ability to auto-generate Full XCI hashes, (v1.5) added a button that saves your preferred default dumper and tool values, (v1.4) added a dropdown for the tool menu, (v1.4) fixed regression from v1.3, fixed NX Game Info title and version importing, now supports CSV imports from NX Game Info (File -> Export -> CSV), now imports the entire title line, now chooses the base Title ID as Game ID instead of the latest one, now removes any punctuation not compliant with No-Intro and changes colons into dashes, now excludes any parentheses present in the update column

# To-do
- TESTING
- Add redump auto-detection and auto-fill from integrated DATs
- Integrate NX Game Info Control NACP parsing functionality directly without dependencies
- Fix bug where newly-applied merged versions / updates via 4 6 1 6 don't take precedence
- Add multi-title cart support
- Add separate mode for Scene / P2P XCI submissions
- Further polish, like a progress window for hash calculation and Full XCI generation
- Compile into a user-friendly EXE with all dependencies bundled in
- Add support for other systems? 👀

**NOTE NOTE NOTE this is in EARLY ALPHA and has been MINIMALLY TESTED so it may BREAK at any time for any reason, use at your own risk and double check its output!**

# Readme

So, you want to submit a Switch cart to No-Intro? I developed a quick and easy Python script which standardizes forum submissions into easily-imported XML files.

First, dump your cart using the latest version of [nxdumptool-rewrite](https://github.com/DarkMatterCore/nxdumptool/releases) onto your SD card or to your PC via USB using the default dump settings.

Note, the default dump settings are as follows:
- prepend key area: no
- keep certificate: no
- trim dump: no
- calculate checksum: yes

Within nxdumptool select the following options which will dump each file to your SD card / PC via USB:
- dump gamecard image (xci)
- dump gamecard initial data
- dump gamecard id set

You can dump the Certificate as well, but that is not needed for a No-Intro submission because it contains all of the personalized metadata unique to your cart, and No-Intro only catalogues reproducible metadata. Dumping the UID / header / cardinfo / HFS partitions are also not necessary here, although feel free to do so if you want.

Move your files to your PC and concatenate the XCIs if necessary. You should have three files that look something like this:

- Fast & Furious Spy Racers - Rise of SH1FT3R 1.0.2 [010034C013624000][v0] (Card ID Set) (6CD8FDA1).bin
- Fast & Furious Spy Racers - Rise of SH1FT3R 1.0.2 [010034C013624000][v0] (Initial Data) (57A3A06C).bin
- Fast & Furious Spy Racers - Rise of SH1FT3R 1.0.2 [010034C013624000][v0] [NKA][NC][NT].xci

Once you do, you're ready to begin using my tool.

You can download the script [here](https://raw.githubusercontent.com/rarenight/No-Intro-Switch-Cart-Submission-Tool/main/no-intro-switch-cart-submission-tool-v1.7.py) (right click -> Save As).

You'll need Python with the PyQt5 dependency installed (`pip install pyqt5`) along with the [NX Game Info](https://github.com/garoxas/NX_Game_Info) CLI executable and its libraries in the same directory as the script before you get started.

First open my script, click "Automatically Import Metadata", and drag and drop the Default XCI file into the window. **NOTE: THIS IMPORT TOOL DOES NOT SUPPORT FULL XCIS OR MULTI-TITLE CARTS YET.** The values will auto-populate:

![image](https://github.com/user-attachments/assets/7450a41d-50f1-47f7-a34d-532047290251)

You'll (hopefully) see the Game Name, Languages, and GameID1 auto-populated. It should also auto-populate the Version and Update in the File Info tab. If for whatever reason the metadata import messes up, you can always manually type or adjust the values. 

Select the applicable cart region from the dropdown. You can find the region info on the last three digits of the serial that's on the front of your cart, which would be -USA in this case:

![image](https://github.com/user-attachments/assets/d1b70802-24ae-4c4a-bb8c-bd28291db7f7)

(Note: Nintendo-published carts are considered to be "World" and are an exception to the region rule)

Then click the Dump Info tab, fill out the Dumper and Tool fields (there's a dropdown as well with common dump tool names), and click "Set Default Dumper and Tool" if you want those values to remain constant. Then click "Generate Card ID Values". Drag and drop the (Card ID Set) binary file that nxdumptool outputs into the window and the Card ID values should (hopefully) populate like this:

![image](https://github.com/user-attachments/assets/15db1465-5a7f-460c-b3fd-d1196b0a41cf)

A custom dump date can be specified if your cart wasn't dumped the same day.

Then click the Media Info tab and fill out all the values manually. A dropdown menu allows you to select a downwards triangle for your convenience.

![image](https://github.com/user-attachments/assets/aa24b957-0408-46b8-967b-10138c9cd78a)

You can select "Loose Cart" if you don't have an original box for your cart.

Click the File Info tab and then "Import Hashes."

Drag and drop the Initial Area (aka Initial Data) BIN file, then the Default XCI file into the window and their hashes will auto-populate. My program automatically generates the Full XCI hashes without having to create the file separately. Please note this takes a while for large files and the program appears to freeze while it's hashing, please be patient.

![image](https://github.com/user-attachments/assets/925c5cd9-bb47-493c-a36c-085cae68dcf5)

My program also offers the option to generate a Full XCI file if you'd like a local copy for your collection, as well as the option to truncate a Full XCI back to its original Default XCI and Initial Area.

When all fields are populated as shown in the above image, click "Generate Submission" and an XML file will be generated in your chosen directory.

This program generates an XML submission file that looks like this:

![image](https://github.com/user-attachments/assets/6ba5ca81-21ae-453f-a038-6c76ca7620f4)

This XML submission file can then be easily imported into No-Intro's backend in a standardized and uniform format:

![image](https://github.com/user-attachments/assets/6fccc898-132a-4b50-81e0-5187a5e6edf8)

![image](https://github.com/user-attachments/assets/2fc094fa-6c12-4580-b9ac-3f22d6476cdf)
