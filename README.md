# User Submission Tutorial

So you want to submit a Switch cart to No-Intro? I developed a quick and easy Python script which standardizes forum submissions into easily-imported XML files. It can also create a Full XCI via drag and drop and convert a Full XCI back to its Default XCI + Initial Area components.

First, dump your cart using the latest version of [nxdumptool-rewrite](https://github.com/DarkMatterCore/nxdumptool/releases) onto your SD card or to your PC via USB using the default dump settings.

The default dump settings are as follows:
- prepend key area: no
- keep certificate: no
- trim dump: no
- calculate checksum: yes

Within nxdumptool select the following options which will dump each file to your SD card or ideally to your PC directly via USB:
- dump gamecard image (xci)
- dump gamecard initial data
- dump gamecard id set

You can dump the Certificate as well, but that is not needed for a No-Intro submission because it contains all of the personalized metadata unique to your cart, and No-Intro only catalogues reproducible metadata. Dumping the UID / header / cardinfo / HFS partitions are also not necessary here, although feel free to do so if you want.

Move your dumped game files to your PC and concatenate the XCIs if necessary. You should have three files that look something like this:

- Fast & Furious Spy Racers - Rise of SH1FT3R 1.0.2 [010034C013624000][v0] (Card ID Set) (6CD8FDA1).bin
- Fast & Furious Spy Racers - Rise of SH1FT3R 1.0.2 [010034C013624000][v0] (Initial Data) (57A3A06C).bin
- Fast & Furious Spy Racers - Rise of SH1FT3R 1.0.2 [010034C013624000][v0] [NKA][NC][NT].xci

Once you do, you're ready to begin using my tool.

You can download the script in the [releases](https://github.com/rarenight/No-Intro-Switch-Cart-Submission-Tool/releases/tag/v2.5) section. It includes a pre-built version of the [hactoolnet](https://github.com/shloop/LibHac/tree/master) fork and all dependencies you'll need to run the Python script, including Linux versions. Unrar is provided for Windows but if using Linux, choose the corresponding version from their [website](https://www.rarlab.com/rar_add.htm) that fits your distro. Note to run the automatic import function, you'll need .NET installed and you need to place up-to-date `prod.keys` in the same directory as the script.

You'll also need Python with the PyQt6 dependency installed (`pip install pyqt6` and `pip install rarfile` or just install the `requirements.txt`). Your directory should look like this before running the script for the first time:

![image](https://github.com/user-attachments/assets/6f53a0d6-928d-4406-a0e2-3a001b34c11d)

To get started, open my script, click "Automatically Import Metadata", and drag and drop the XCI file into the window. Both Default XCIs and Full XCIs are now supported for automatic import.

![image](https://github.com/user-attachments/assets/e95daf33-26d1-440b-ba2b-d26f97c984f1)

When dragged and dropped, the values will auto-populate into the textboxes.

If you can't get the automatic import function working, simply open the game (Default XCIs only for manual importing) in [NX Game Info](https://github.com/garoxas/NX_Game_Info/tree/master) GUI instead and click File -> Export as a CSV file:

![image](https://github.com/user-attachments/assets/7444327f-edc8-4952-bfae-7e03216bb8c2)

Then click "Manually Import Metadata" and drag and drop the CSV file to the top of the window. The values will auto-populate:

![image](https://github.com/user-attachments/assets/5ad1c85c-3ddd-40a8-9a32-57188326df4a)

Or run nxgameinfo_cli.exe on the file:

![image](https://github.com/user-attachments/assets/37499f1a-e9b7-4a41-802b-e254497d822f)

And copy and paste the values into the window:

![image](https://github.com/user-attachments/assets/b2a03a8e-431a-4249-a687-f2334a07ed8d)

Either way, when you import the metadata either automatically or manually, the Game Name, Languages, GameID1, along with Version and Update in the File Info tab should all be auto-populated.

If for whatever reason the metadata import messes up, you can always manually type or adjust the values. You can ignore the "Scene Release" checkbox if you're submitting a personal dump. If you're adding scene release, check it and skip to the Scene Release section at the bottom.

Select the applicable cart region from the dropdown. You can find the region info on the last three digits of the serial that's on the front of your cart, which would be -USA in this case:

![image](https://github.com/user-attachments/assets/d1b70802-24ae-4c4a-bb8c-bd28291db7f7)

(Note: All Nintendo-published carts are considered to be "World" and are the sole exception to the region rule)

When imported the window should look like this:

![image](https://github.com/user-attachments/assets/ef0aca64-a2e1-4cfe-a65f-d343f7566d25)

Then click the Dump Info tab, fill out the Dumper and Tool fields (there's a dropdown as well with common dump tool names), and click "Set Default Dumper and Tool" if you want those values to remain constant. Then click "Generate Card ID Values". Drag and drop the (Card ID Set) binary file that nxdumptool outputs into the window and the Card ID values should (hopefully) populate like this:

![image](https://github.com/user-attachments/assets/84519754-1706-4079-990c-5a761b6afb0b)

A custom dump date can be specified if your cart wasn't dumped the same day.

Then click the Media Info tab and fill out all the values manually. A dropdown menu allows you to select a downwards triangle for your convenience.

![image](https://github.com/user-attachments/assets/f60b46aa-69df-4642-b7f4-cbb3b3b50243)

You can select "Loose Cart" if you don't have an original box for your cart.

Click the File Info tab and then "Calculate Hashes".

Drag and drop the Initial Area (aka Initial Data) BIN file, then the Default XCI file into the window and their hashes will auto-populate. My program automatically generates the Full XCI hashes without having to create the file separately. Please note this takes a while for large files and the program appears to freeze while it's hashing, please be patient. When done all textboxes will be filled out like this and the Generate Submission button will become enabled:

![image](https://github.com/user-attachments/assets/cbcdaac9-cd87-4b78-b6d8-fdad55212158)

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
- The Initial Data file, uploaded either as a file or encoded into Base64 using [Cryptii](https://cryptii.com/pipes/base64-to-hex)
- Ideally hactoolnet's output when you provide the command "hactoolnet -t xci --listtitles Input.xci"
- Any images you wish to submit as well


# Scene Release Submission Tutorial

This is for advanced users who want to easily import new scene releases into No-Intro.

When you click the "Scene Release" checkbox, a new Scene Cart tab becomes enabled. In order for the script to parse a scene release correctly, you need to select an unmodified Scene Directory with a .nfo file and a .sfv file all present in the original scene directory like this:

![image](https://github.com/user-attachments/assets/37391fa5-3391-4ca7-acea-eda274fa1653)

Once selected, these options will be enabled:

![image](https://github.com/user-attachments/assets/8113f105-342d-4a64-8038-c24fe8abd597)

Make sure to set the applicable scene group or type in a custom one as needed. Note: P2P groups like KTHNX are not supported.

Open NFO opens the NFO file in a separate text window so you can easy view and copy data as needed:

![image](https://github.com/user-attachments/assets/2cf60a04-d107-43f7-b0ba-867b8a237fe1)

Verify Scene RARs uses a built-in verification module along with the SFV file to verify that all scene RARs are valid:

![image](https://github.com/user-attachments/assets/36619913-c3ae-4d87-bd86-8f971f823689)

Extract RARs uses unrar (must be in the same directory as the script) to automatically extract all scene RARs. The directory will look like this when extracted with the XCI in the same directory:

![image](https://github.com/user-attachments/assets/018dbcfb-129c-4895-a785-4e2dda1b7e75)

Check "Keep Scene RARs" if you wish to preserve the original scene RARs for whatever reason.

Once you extract the XCI, you can then continue onto the other tabs. Fill out Game Info and Media Info to the best of your abilities, and import the hashes for the Default XCI. The Dump Info and Initial Area and Full XCI fields have been disabled for your convenience. The XML file it generates will be tailor-made for an easy scene release import:

![image](https://github.com/user-attachments/assets/02e37699-b4dc-4c6d-9b39-f292d909687b)

![image](https://github.com/user-attachments/assets/8e2c518d-9798-452b-9ca2-2d5ddf39d00d)


# Versions

v2.5 - 2024-08-18
- (v2.5) Replaced NX Game Info with a native hactoolnet implementation for deriving embedded metadata, Added auto-import support for multi-title XCIs and full XCIs, Upgraded to PyQt6 with dark mode support, Fixed UTF-8 Japanese character bug, Added scene RAR auto-extraction
- (v2.2) Further performance optimizations to minimize out-of-memory crashes, Reintroduced manual import option for users who can't get the EXE dependency to work
- (v2.1) Fixed Exclude Initial Area bug, Fixed a few regressions from v2.0
- (v2.0) Added scene cart mode, Now processes files in 4 MB chunks to minimize crashing on low-end machines, Added processing percentage in terminal
- (v1.8) Embedded nxgameinfo_cli as a dependency, Added a "Truncate FullXCI File" button that reverts a Full XCI back to a Default XCI and an Initial Area, Added additional failsafes to prevent Default XCIs / Full XCIs from being mistakenly processed
- (v1.7) Added a dropdown for regions, Fixed GameID2 four-digit bug, Add revision auto-fill, Added loose cart toggle
- (v1.6) Fixed NX Info import glitch where CLI importing wouldn't detect v0, Added directory selection support for Mac + Linux
- (v1.5) Added the ability to auto-generate Full XCI hashes, added a button that saves your preferred default dumper and tool values
- (v1.4) added a dropdown for the tool menu, fixed regression from v1.3
- (v1.3) fixed NX Game Info title and version importing, now supports CSV imports from NX Game Info (File -> Export -> CSV), now imports the entire title line, now chooses the base Title ID as Game ID instead of the latest one, now removes any punctuation not compliant with No-Intro and changes colons into dashes, now excludes any parentheses present in the update column
