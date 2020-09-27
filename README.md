# <div align = "center">Drowsy-Detector</div>

<p align="center">
  <img src="logo.png">
</p>

## ShellHacks Competition


How to run for now:

1. If dependencies haven't been installed run:
```pip install -r requirements.txt```

2. run
```python VideoStreaming/main.py```


## Functions

### Step 1
```get_frame()```
'''
Uses camera to track the users eyes, in case user has eyes closed for more than 15 frames, send ```Alert```.
'''
### Step 2
```
def simulated_user_path(start_address, end_address):
    points = get_points_along_path(API_KEY,start_address,end_address)

    times,coords = [],[]
    for time,geo in points.items():
        times.append(times)
        coords.append(geo)
    
    return times,coords
```
 
### Step 3 
 ```find_places(journey_coords_1,journey_coords_2)``` 
 Gets the users current-coodinates and When Drowsey alert is recieved finds the closest ```gas_station```

### Step 4
```generateRealTimeStats(self)``` :Generates the Drowsy instance vs time graph.


