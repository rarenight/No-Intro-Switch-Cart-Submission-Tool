# Versions

v2.2 - 2024-08-12
- (v2.2) Further performance optimizations to minimize out-of-memory crashes, (v2.2) Reintroduced manual import option for users who can't get the EXE dependency to work, (v2.1) Fixed Exclude Initial Area bug, (v2.1) Fixed a few regressions from v2.0, (v2.0) Added scene cart mode, (v2.0) Now processes files in 4 MB chunks to minimize crashing on low-end machines, (v2.0) Added processing percentage in terminal, (v1.8) Embedded nxgameinfo_cli as a dependency, (v1.8) Added a "Truncate FullXCI File" button that reverts a Full XCI back to a Default XCI and an Initial Area, (v1.8) Added additional failsafes to prevent Default XCIs / Full XCIs from being mistakenly processed, (v1.7) Added a dropdown for regions, (v1.7) Fixed GameID2 four-digit bug, (v1.7) Add revision auto-fill, (v1.7) Added loose cart toggle, (v1.6) Fixed NX Info import glitch where CLI importing wouldn't detect v0, (v1.6) Added directory selection support for Mac + Linux, (v1.5) Added the ability to auto-generate Full XCI hashes, (v1.5) added a button that saves your preferred default dumper and tool values, (v1.4) added a dropdown for the tool menu, (v1.4) fixed regression from v1.3, fixed NX Game Info title and version importing, now supports CSV imports from NX Game Info (File -> Export -> CSV), now imports the entire title line, now chooses the base Title ID as Game ID instead of the latest one, now removes any punctuation not compliant with No-Intro and changes colons into dashes, now excludes any parentheses present in the update column

# To-do
- **TESTING**
- Add redump auto-detection and auto-fill from integrated DATs
- Integrate Control NACP parsing functionality in Python without EXE dependencies
- Fix bug where newly-applied merged versions and updates via 4 6 1 6 don't take precedence
- Add multi-title and FullXCI support when auto-importing
- Compile into a user-friendly EXE with all dependencies bundled in
- Add support for other systems? 👀

# User Submission Tutorial

So, you want to submit a Switch cart to No-Intro? I developed a quick and easy Python script which standardizes forum submissions into easily-imported XML files. It can also create a Full XCI via drag and drop and convert a Full XCI back to its Default XCI + Initial Area components.

First, dump your cart using the latest version of [nxdumptool-rewrite](https://github.com/DarkMatterCore/nxdumptool/releases) onto your SD card or to your PC via USB using the default dump settings.

The default dump settings are as follows:
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

You can download the script [here](https://raw.githubusercontent.com/rarenight/No-Intro-Switch-Cart-Submission-Tool/main/no-intro-switch-cart-submission-tool-v2.2.py) (right click -> Save As).

If you want to use the automatic import function: you'll need Python with the PyQt5 dependency installed (`pip install pyqt5` or just install the `requirements.txt`) along with up-to-date `prod.keys` and [NX Game Info](https://github.com/garoxas/NX_Game_Info) CLI executable and its libraries in the same directory as the script before you get started. Your directory should look like this:

![image](https://github.com/user-attachments/assets/d16f7642-b017-42ff-a5bd-aff61b1a8d29)

If for whatever reason the automatic import function doesn't work, you can also manually import metadata from NX Game Info.

To get started, open my script, click "Automatically Import Metadata", and drag and drop the Default XCI file into the window.

When dragged and dropped, the values will auto-populate.

If you can't get the automatic import function working, simply open the game in NX Game Info GUI and click File -> Export as a CSV file:

![image](https://github.com/user-attachments/assets/7444327f-edc8-4952-bfae-7e03216bb8c2)

Then click "Import Metadata Manually" and drag and drop the CSV file to the top of the window. The values will auto-populate:

![image](https://github.com/user-attachments/assets/928fa7a8-06f1-4d9f-9992-f4b0de8704a5)

Or run nxgameinfo_cli.exe on the file:

![image](https://github.com/user-attachments/assets/4362ed44-15ef-48ca-9c96-d661edf93560)

And copy and paste the values into the window:

![image](https://github.com/user-attachments/assets/f3c13945-ac3e-4d61-abb2-4ec72784faa5)

Either way, when you import the metadata either automatically or manually, the Game Name, Languages, GameID1, along with Version and Update in the File Info tab should all be auto-populated. **NOTE: THIS TOOL DOES NOT SUPPORT IMPORTING FULL XCIS OR MULTI-TITLE CARTS YET. It can only truncate FullXCIs into Default XCIs + Initial Areas for now.** 

If for whatever reason the metadata import messes up, you can always manually type or adjust the values. You can ignore the "Scene Release" checkbox if you're submitting a personal dump. If you're adding scene release, check it and skip to the Scene Release section at the bottom.

Select the applicable cart region from the dropdown. You can find the region info on the last three digits of the serial that's on the front of your cart, which would be -USA in this case:

![image](https://github.com/user-attachments/assets/d1b70802-24ae-4c4a-bb8c-bd28291db7f7)

(Note: Nintendo-published carts are considered to be "World" and are an exception to the region rule)

When imported the window should look like this:

![image](https://github.com/user-attachments/assets/93c1502e-fe25-4281-9f52-c797658beb97)

Then click the Dump Info tab, fill out the Dumper and Tool fields (there's a dropdown as well with common dump tool names), and click "Set Default Dumper and Tool" if you want those values to remain constant. Then click "Generate Card ID Values". Drag and drop the (Card ID Set) binary file that nxdumptool outputs into the window and the Card ID values should (hopefully) populate like this:

![image](https://github.com/user-attachments/assets/1daa3ead-cbbf-49cf-b124-792777e4466f)

A custom dump date can be specified if your cart wasn't dumped the same day.

Then click the Media Info tab and fill out all the values manually. A dropdown menu allows you to select a downwards triangle for your convenience.

![image](https://github.com/user-attachments/assets/7280a502-c006-4821-bf9f-d78963c4351e)

You can select "Loose Cart" if you don't have an original box for your cart.

Click the File Info tab and then "Import Hashes."

Drag and drop the Initial Area (aka Initial Data) BIN file, then the Default XCI file into the window and their hashes will auto-populate. My program automatically generates the Full XCI hashes without having to create the file separately. Please note this takes a while for large files and the program appears to freeze while it's hashing, please be patient.

![image](https://github.com/user-attachments/assets/20ce8a14-4512-43a3-8df6-db46e845d9ec)

If you only have a default XCI, you can uncheck the "Include Initial Area" checkbox and it'll disable the Initial Area and Full XCI requirements. Also on the File Info tab is the option to generate a Full XCI file if you'd like a local copy for your collection, as well as the option to truncate a Full XCI back to its original Default XCI and Initial Area components.

When all fields are populated as shown in the above image, click "Generate Submission" and an XML file will be generated in your chosen directory.

This program generates an XML submission file that looks like this:

![image](https://github.com/user-attachments/assets/6ba5ca81-21ae-453f-a038-6c76ca7620f4)

This XML submission file can then be easily imported into No-Intro's backend in a standardized and uniform format:

![image](https://github.com/user-attachments/assets/6fccc898-132a-4b50-81e0-5187a5e6edf8)

![image](https://github.com/user-attachments/assets/2fc094fa-6c12-4580-b9ac-3f22d6476cdf)

You can apply for a No-Intro forum account and then submit dumps [here](https://forum.no-intro.org/viewforum.php?f=7).

When creating a Switch cart submission to No-Intro, please upload the following:
- The XML submission file that my tool outputs
- The Initial Data metadata file, uploaded either as a file or encoded into Base64 using Cryptii
- Ideally hactoolnet's output when you provide the command "hactoolnet -t xci --listtitles Input.xci"
- Any images you wish to submit as well

# Scene Release Submission Tutorial

This is for advanced users who want to easily import new scene releases into No-Intro.

When you click the "Scene Release" checkbox, a new Scene Cart tab becomes enabled. In order for the script to parse a scene release correctly, you need to select an unmodified Scene Directory with a .nfo file and a .sfv file all present in the original scene directory like this:

![image](https://github.com/user-attachments/assets/37391fa5-3391-4ca7-acea-eda274fa1653)

Once selected, these options will be enabled:

![image](https://github.com/user-attachments/assets/8b9efde5-425f-4402-81ac-4f6329ab9728)

Make sure to set the applicable scene group or type in a custom one as needed. Note: P2P groups like KTHNX are not supported.

Open NFO opens the NFO file in a separate text window so you can easy view and copy data as needed:

![image](https://github.com/user-attachments/assets/0fd4e557-e464-4392-aec3-7def0ecce5b3)

Verify Scene RARs uses a built-in verification module along with the SFV file to verify that all scene RARs are valid:

![image](https://github.com/user-attachments/assets/97211dd8-7a6e-427a-8e92-68677dba8246)

Once you extract the XCI, you can then continue onto the other tabs. Fill out Game Info and Media Info to the best of your abilities, and import the hashes for the Default XCI. The Dump Info and Initial Area and Full XCI fields have been disabled for your convenience. The XML file it generates will be tailor-made for an easy scene release import:

![image](https://github.com/user-attachments/assets/02e37699-b4dc-4c6d-9b39-f292d909687b)

![image](https://github.com/user-attachments/assets/8e2c518d-9798-452b-9ca2-2d5ddf39d00d)
