# Engineering_Toolbox
An engineering toolbox with some powerful calculators and data scrapers.

## material_data_scraper.py
This script can be run independently from the pipe_stress_metric calculator.py script. It is intended to be cross-functional with any outside script.

I originally came up with the idea for a scraper since the materials package on PyPi, to put it lightly, is extremely limiting. Here is the link: https://pypi.org/project/materials/ 
Matminer is currently an API that exists, but:
1. You need an API key to use it. It's currently free, but man is it cumbersome.
2. The material properties available are frankly useless for actual engineering work.
3. There is no good search method within the API.
Here is the link: https://matminer.readthedocs.io/en/latest/

I also wanted to avoid Selenium solutions, as they're far clunkier, and some machines have restrictions on what you can reference for work tasks, including APIs.

Since there was no good method to procure actually useful engineering data, I figured I'd do it myself.

The script parses through MatWeb to determine material properties. MatWeb is THE material repository- SolidWorks, COMSOL, Autodesk, Ansys all borrow its data.
Provided a search term, it will compile a list of the top 50 materials present in MatWeb's repository, then choose the one that best fits the search term.

To create this list, it's a bit janky. I don't have a MatWeb membership (nor do I expect actual users of my code to have one either), so instead I use pdfkit & the wkhtmltopdf binary to convert the headless webpage into a pdf. This pdf is then interpreted by pdfplumber to convert into a .csv and Pandas dataframe, with a bit of post-processing to fix formatting issues generally.

I'm considering a version of this tool that doesn't require this extra step or play around with PATH variables, but I've yet to find a package that can do that (or develop my own).

### Running as its own script
To run this script independently:

    python material_data_scraper.py <your material of choice>

The script references the argument as one string, so I'd write a material along the lines of:

    python material_data_scraper.py Aluminum_6061

### Useful functions to reference
The most important functions to reference from this script, if you want to use it in conjuction with your own, are:
  - retrieve_material_data: Allows you to get the MatWeb material characteristics. Example call:

        material_data = retrieve_material_data(material_name)

     If you were to try, as another example:

        retrieve_material_data("Aluminum_6061")

    You'd see something akin to:
        
        Best match based on Levenshtein distance: Aluminum 6061-O - https://www.matweb.com/search/DataSheet.aspx?MatGUID=626ec8cdca604f1994be4fc2bc6f7f63

  - retrieve_material_data_verbose: Works the same as retrieve_material_data, only you get to see the top 50 MatWeb matches as per your query. Example call:

        material_data = retrieve_material_data(material_name)

    If you were to try, as another example:

        retrieve_material_data_verbose("Aluminum_6061")

    You'd see something akin to:
    
        1. Aluminum 6061A Composition Spec - https://www.matweb.com/search/DataSheet.aspx?MatGUID=98d7fcd57e3845d68124c1bc4376618a
        2. Alclad Aluminum 6061-O - https://www.matweb.com/search/DataSheet.aspx?MatGUID=6c41b0bdea564d20b9fd287c03c97923
        3. Alclad Aluminum 6061-T4, T451 - https://www.matweb.com/search/DataSheet.aspx?MatGUID=1318cc5c380f46e59cd00339fb7d3a91
        4. Alclad Aluminum 6061-T6, T651 - https://www.matweb.com/search/DataSheet.aspx?MatGUID=3a2e111b27ef4e5d813bad6044b3f318
        5. Aluminum 6061-O - https://www.matweb.com/search/DataSheet.aspx?MatGUID=626ec8cdca604f1994be4fc2bc6f7f63
        6. Aluminum 6061-T4; 6061-T451 - https://www.matweb.com/search/DataSheet.aspx?MatGUID=d5ea75577b1b49e8ad03caf007db5ba8
        7. Aluminum 6061-T6; 6061-T651 - https://www.matweb.com/search/DataSheet.aspx?MatGUID=b8d536e0b9b54bd7b69e4124d8f1d20a
        8. Aluminum 6061-T8 - https://www.matweb.com/search/DataSheet.aspx?MatGUID=90404a0c001c4016b2b359a6c19f9127
        9. Aluminum 6061-T91 - https://www.matweb.com/search/DataSheet.aspx?MatGUID=e6212a3df98d4a7eb51edc1b1d3927ed
        10. Aluminum 6061-T913 - https://www.matweb.com/search/DataSheet.aspx?MatGUID=0f6b9e4702884eadbe6a8450cf89a925
        
        Best match based on Levenshtein distance: Aluminum 6061-O - https://www.matweb.com/search/DataSheet.aspx?MatGUID=626ec8cdca604f1994be4fc2bc6f7f63
    
  - levenshtein_distance: Allows you to calculate the Levenshtein distance between 2 strings to compare how likely one is to match the other. The smaller the distance, the more likely. You could use a different library for string matching, but it's much faster to implement a local algorithm. It is not necessary to import this in addition to retrieve_material_data. Example call:

        distance = levenshtein_distance("Yield Strength", "Feet")

## pipe_stress_metric.py

This calculates the stress of a continuous tube based on a few user inputs (which of course, should be written in metric units).

This also uses CoolProp to import fluid properties, like viscosity, upon simple material calls like "Water".

By default, these are the various queries:

    Enter the outer diameter of the pipe (in meters) [default: 1]:
    Enter the thickness of the pipe (in meters) [default: 0.01]:
    Enter the length of the pipe (in meters) [default: 100]:
    Enter the fluid type [default: Water]:
    Enter the fluid temperature (in K) [default: 298.15]:
    Enter the tubing material [default: Copper]:
    Enter the safety factor [default: 1.0]:
    Enter the external pressure (in Pa) [default: 101325 Pa]:
    Enter the flow rate (in m³/s) [default: 100]:
    Enter the internal pressure (in Pa) [default: 1013250 Pa]:
    Does the pipe have bends? (Y/N) [default: N]:

The stress is calculated based on well known formulae and takes into account shape factors formed by tube bends. This stress is then compared to the yield stress foumd through the data collected by material_data_scraper.py to determine whether the design passes or fails. The default parameters should fail.


![3-s2 0-B9780123868886000018-f01-04-9780123868886](https://github.com/user-attachments/assets/8ceaa2b6-9d46-4d7c-9551-4207a0ae8cdd)

![zs4G3](https://github.com/user-attachments/assets/f9241c22-bf49-45e1-a2ef-bcaedd2557a5)


Note that if the pipe has a bend, the shape factor is determined by the bend radius Rb. r_m is the mean radius, as shown.

![image](https://github.com/user-attachments/assets/b20d4450-6244-4c14-9b58-8d9bf8bb6fdf)

## Sources:
  - https://www.matweb.com/
  - https://wkhtmltopdf.org/
  - https://physics.stackexchange.com/questions/503465/using-height-to-calculate-pressure-independent-variable-and-flow-rate-depende
  - https://www.sciencedirect.com/topics/engineering/hoop-stress
  - https://www.comsol.com/blogs/the-intriguing-stresses-in-pipe-bends

## Installing packages and binaries
Run the following command:

    pip install -r requirements.txt

Additionally, run the wkhtmltox-0.12.6-1.msvc2015-win64.exe executable (works for Windows). This is to download the wkhtmltopdf binaries, which can also be found here: https://wkhtmltopdf.org/downloads.html

The path on a Windows machine should be C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe by default.
However, if for some reason this is not true for your machine, the path is modifiable in material_data_scraper.py on ~line 104.


## Troubleshooting
  - Nothing comes up for my chosen material. What gives?
      - Check the provided link if there happens to be a hit. If the link shows missing/no properties, there you go. Otherwise, it may just not be in MatWeb.
      - Here's an example: https://www.matweb.com/search/DataSheet.aspx?MatGUID=74f8eff7027c41fab63ba1fb08718056
  - What's with this snippet:
    - Error converting webpage to PDF: wkhtmltopdf reported an error:
    - QNetworkReplyImplPrivate::error: Internal problem, this method must only be called once.
    - libpng warning: IDAT: Too much image data
    - Exit with code 1 due to network error: RemoteHostClosedError
    - That's probably due to the use of a VPN- too many nodes can cause multiple references as shown here. This does not affect the actual output of the script- it references the first instance and you'll get your data.

  
