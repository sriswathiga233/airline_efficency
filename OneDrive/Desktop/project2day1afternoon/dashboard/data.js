// Extracted data from outputs CSVs for static dashboard
const DATA = {
  kpis: {
    total_flights: 1000,
    avg_load_factor: 81.6,
    avg_utilisation: 73.6,
    aircraft_types: 6,
    routes: 20
  },
  aircraft_load: {
    labels: ['ATR 72','A320','B737-800','A321','B787','A350'],
    values: [84.039352,83.550084,83.147629,80.700665,76.010425,73.951648]
  },
  aircraft_util: {
    labels: ['ATR 72','A320','A321','B737-800','B787','A350'],
    values: [77.928168,74.862362,73.959791,73.751423,68.202352,66.312799]
  },
  // three lowest-occupancy routes (explicit)
  lowest_routes: [
    {route: 'Mumbai-Kolkata', value: 70.71},
    {route: 'Hyderabad-Kolkata', value: 70.97},
    {route: 'Chennai-Kolkata', value: 72.22}
  ],
  // inefficient combinations (first 35 from CSV)
  ineff: [
    {Aircraft_Type:'A350',Route:'Chennai-Kolkata',avg_load:62.666666666666664,avg_util:62.09647913501868,flights:3},
    {Aircraft_Type:'A350',Route:'Hyderabad-Kolkata',avg_load:63.28205128205128,avg_util:61.61003543425414,flights:3},
    {Aircraft_Type:'B787',Route:'Hyderabad-Kolkata',avg_load:67.58620689655172,avg_util:62.20695824589036,flights:10},
    {Aircraft_Type:'A350',Route:'Mumbai-Singapore',avg_load:67.81538461538462,avg_util:80.15255068391659,flights:5},
    {Aircraft_Type:'B787',Route:'Chennai-Delhi',avg_load:68.62068965517241,avg_util:71.24350907494426,flights:3},
    {Aircraft_Type:'A321',Route:'Mumbai-Kolkata',avg_load:69.5104895104895,avg_util:75.61151361616766,flights:13},
    {Aircraft_Type:'A320',Route:'Mumbai-Kolkata',avg_load:69.86111111111111,avg_util:76.91655166282003,flights:12},
    {Aircraft_Type:'B787',Route:'Mumbai-Kolkata',avg_load:69.86206896551724,avg_util:66.66223647758406,flights:5},
    {Aircraft_Type:'A350',Route:'Chennai-Delhi',avg_load:69.96923076923078,avg_util:66.37723850041425,flights:5},
    {Aircraft_Type:'B787',Route:'Chennai-Kolkata',avg_load:71.55172413793103,avg_util:62.92499960260473,flights:4},
    {Aircraft_Type:'A350',Route:'Delhi-Kolkata',avg_load:72.07692307692308,avg_util:60.73986430230862,flights:4},
    {Aircraft_Type:'A350',Route:'Chennai-Hyderabad',avg_load:73.38461538461539,avg_util:45.00778974463185,flights:2},
    {Aircraft_Type:'B787',Route:'Mumbai-Bengaluru',avg_load:73.5632183908046,avg_util:53.11086855545108,flights:3},
    {Aircraft_Type:'B787',Route:'Delhi-Hyderabad',avg_load:73.94088669950739,avg_util:62.951130797587666,flights:7},
    {Aircraft_Type:'B787',Route:'Chennai-Mumbai',avg_load:74.34482758620689,avg_util:61.976366257669305,flights:5},
    {Aircraft_Type:'A350',Route:'Delhi-Hyderabad',avg_load:74.41025641025641,avg_util:60.99302429123862,flights:6},
    {Aircraft_Type:'A350',Route:'Chennai-Mumbai',avg_load:74.92307692307692,avg_util:59.84054569567331,flights:4},
    {Aircraft_Type:'B787',Route:'Bengaluru-Hyderabad',avg_load:77.41379310344828,avg_util:43.83098591549296,flights:2},
    {Aircraft_Type:'A350',Route:'Mumbai-Delhi',avg_load:79.17948717948718,avg_util:58.769438071306304,flights:3},
    {Aircraft_Type:'A350',Route:'Mumbai-Bengaluru',avg_load:80.49230769230769,avg_util:52.82034642107509,flights:5},
    {Aircraft_Type:'B787',Route:'Mumbai-Delhi',avg_load:81.03448275862068,avg_util:63.63636363636363,flights:1},
    {Aircraft_Type:'A321',Route:'Chennai-Hyderabad',avg_load:81.4935064935065,avg_util:50.93991797002728,flights:14},
    {Aircraft_Type:'B737-800',Route:'Chennai-Hyderabad',avg_load:82.24573780129336,avg_util:55.83420180905802,flights:18},
    {Aircraft_Type:'B787',Route:'Delhi-Kolkata',avg_load:84.13793103448275,avg_util:64.09764216662265,flights:6},
    {Aircraft_Type:'A320',Route:'Chennai-Hyderabad',avg_load:85.50925925925925,avg_util:57.65262449839977,flights:12},
    {Aircraft_Type:'ATR 72',Route:'Chennai-Hyderabad',avg_load:86.32478632478632,avg_util:61.72724963166882,flights:13},
    {Aircraft_Type:'A321',Route:'Bengaluru-Hyderabad',avg_load:87.87878787878788,avg_util:52.13942378746847,flights:3},
    {Aircraft_Type:'ATR 72',Route:'Chennai-Bengaluru',avg_load:88.4920634920635,avg_util:58.61167115167662,flights:7},
    {Aircraft_Type:'B737-800',Route:'Bengaluru-Hyderabad',avg_load:88.52513227513228,avg_util:56.39261144485876,flights:16},
    {Aircraft_Type:'A320',Route:'Bengaluru-Hyderabad',avg_load:90.43650793650794,avg_util:54.473072973917674,flights:14},
    {Aircraft_Type:'A321',Route:'Chennai-Bengaluru',avg_load:91.51515151515152,avg_util:43.344317850525705,flights:6},
    {Aircraft_Type:'ATR 72',Route:'Bengaluru-Hyderabad',avg_load:91.66666666666667,avg_util:64.83489910871248,flights:5},
    {Aircraft_Type:'B737-800',Route:'Chennai-Bengaluru',avg_load:92.40585122938064,avg_util:50.735840394881386,flights:17},
    {Aircraft_Type:'A320',Route:'Chennai-Bengaluru',avg_load:92.82407407407408,avg_util:48.24567848937022,flights:12},
    {Aircraft_Type:'B787',Route:'Chennai-Bengaluru',avg_load:96.89655172413794,avg_util:36.279069767441854,flights:1}
  ],
  correlation: {
    route_distance_vs_utilisation: 0.738705
  },
  ml: {
    r2: 0.014786290202155494,
    mae: 7.393779318315269,
    rmse: 9.201331671073984,
    coefficients: {
      Route_Distance: -0.009357859093490769,
      Flight_Duration: 6.342022140733181,
      Turnaround_Time: -4.920785785303035,
      Passenger_Capacity: -0.02110011149004798
    },
    intercept: 88.62888460823908
  }
};
