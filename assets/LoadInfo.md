## Family Photo Organiser

## About The Project

The Dashboard is designed to allow for quick navigation and cataloguing of family photos.

### Built With

The Dashboard was constructed using the following libraries and tools,
* [Dash](https://plotly.com/dash/)

* [Bootstrap](https://getbootstrap.com/)

* [Python](https://www.python.org/)

## Run
To start up server use run the python script.

1. Run,
   ```
   python app.py
   ```
   
The following comand line options are,
*  *--local*

  True: Run with local access to server only
  False: Run with network assess
	
  Default: True

  IP address in both cases are printed to terminal
*  *--port*

  int: Port number to be used
  
  Default: 8050
*  *--debug*

  True: Enable Flask debug mode
  False: Disable Flask debug mode

  Default: False
  
## Usage

1. Select the album folder using the ```Pick photo path``` text box or button

2. Select the photo using the ```Photo``` dropdown, "Prev" or "Next" button to navigate between them

3. It is now possible to fill out photo metadata for the photo,
  * ```Title```: Type in the textbox
  * ```Date```: Type in the textbox to select a year, the pick from the datepicker
  * ```Location```: Type in the textbox 
  * ```People```: Click on the photo and use ```Name``` textbox below the image then ```Add```. People can be removed using the ```Delete``` button
  * ```Caption```: Type in the textbox
  * ```Complete```: Tick the tick box, completed photos are coloured green in the dropdown and uncompleted marked in amber
  
4. When happy the ```submit```button will save the metadata to an excel file located in the ```Pick photo path``` directory. 

```Clear``` will empty the form so the user may start afresh.

  

## License

Distributed under the MIT License. See `LICENSE` for more information.



## Contact

For any issues or questions contact Joseph Walker at j.j.walker@durham.ac.uk.

Project Link: [https://github.com/sephwalker321/PhotoOrganiser](https://github.com/sephwalker321/PhotoOrganiser)
