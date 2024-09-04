# Engineering_Toolbox
An engineering toolbox with some powerful calculators and data scrapers. Keeping engineering free!

## material_data_scraper.py
This script can be run independently from the pipe_stress_metric calculator.py script. It is intended to be cross-functional with any outside script.

I originally came up with the idea for a scraper since the materials package on PyPi, to put it lightly, is extremely limiting. Here is the link: https://pypi.org/project/materials/ 
Matminer is currently an API that exists, but:
1. You need an API key to use it. It's currently free, but man is it cumbersome.
2. The material properties available are frankly useless for actual engineering work.
3. There is no good search method within the API.
Here is the link: https://matminer.readthedocs.io/en/latest/

Since there was no good method to procure actually useful engineering data, I figured I'd do it myself.

The script parses through MatWeb to determine material properties. MatWeb is THE material repository- SolidWorks, COMSOL, Autodesk, Ansys all borrow its data.
Provided a search term, it will compile a list of the top 50 materials present in MatWeb's repository, then choose the one that best fits the search term.

To create this list, it's a bit janky. I don't have a MatWeb membership (nor do I expect actual users of my code to have one either), so instead I use pdfkit & the wkhtmltopdf binary to convert the headless webpage into a pdf. This pdf is then interpreted by pdfplumber to convert into a .csv and Pandas dataframe, with a bit of post-processing to fix formatting issues generally.

### Running as its own script
To run this script independently:

    python material_data_scraper.py <your material of choice>

The script references the argument as one string, so I'd write a material along the lines of:

    python material_data_scraper.py Aluminum_6061

### Useful functions to reference
The most important functions to reference from this script, if you want to use it in conjuction with your own, are:
  - retrieve_material_data: Allows you to get the MatWeb material characteristics. Example call:

        material_data = retrieve_material_data(material_name)
  - levenshtein_distance: Allows you to calculate the Levenshtein distance between 2 strings to compare how likely one is to match the other. The smaller the distance, the more likely. You could use a different library for string matching, but it's much faster to implement a local algorithm. It is not necessary to import this in addition to retrieve_material_data. Example call:

        levenshtein_distance("Yield Strength", "Feet")

## pipe_stress_metric.py

This calculates the stress of a continuous tube based on a few user inputs (which of course, should be written in metric units).

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


Note that if the pipe has a bend, the shape factor is determined by the bend radius.

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

  
