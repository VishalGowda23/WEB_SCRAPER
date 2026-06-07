export const MAHARASHTRA_GEO = {
  "Mumbai": [19.0760, 72.8777],
  "Pune": [18.5204, 73.8567],
  "Nagpur": [21.1458, 79.0882],
  "Thane": [19.2183, 72.9781],
  "Nashik": [19.9975, 73.7898],
  "Aurangabad": [19.8762, 75.3433],
  "Solapur": [17.6599, 75.9064],
  "Kolhapur": [16.7050, 74.2433],
  "Amravati": [20.9320, 77.7523],
  "Navi Mumbai": [19.0330, 73.0297],
  "Sangli": [16.8524, 74.5815],
  "Malegaon": [20.5537, 74.5265],
  "Jalgaon": [21.0077, 75.5626],
  "Akola": [20.7059, 77.0019],
  "Latur": [18.4088, 76.5604],
  "Dhule": [20.9042, 74.7749],
  "Ahmednagar": [19.0952, 74.7496],
  "Chandrapur": [19.9615, 79.2961],
  "Parbhani": [19.2644, 76.7729],
  "Ichalkaranji": [16.6974, 74.4619],
  "Jalna": [19.8297, 75.8800],
  "Nanded": [19.1383, 77.3210],
  "Satara": [17.6805, 74.0183],
  "Ratnagiri": [16.9902, 73.3120],
  "Osmanabad": [18.1853, 76.0419],
  "Wardha": [20.7453, 78.6022],
  "Yavatmal": [20.3888, 78.1204],
  "Beed": [18.9901, 75.7531],
  "Gondia": [21.4624, 80.2210],
  "Hinganghat": [20.5599, 78.8415]
};

// Add slightly random offset to prevent exact overlapping of pins in the same city
export const getOffsetCoordinates = (cityName) => {
  const base = MAHARASHTRA_GEO[cityName];
  if (!base) return [19.0760, 72.8777]; // Fallback to Mumbai

  // Offset by up to ~2km (±0.02 degrees)
  const latOffset = (Math.random() - 0.5) * 0.04;
  const lngOffset = (Math.random() - 0.5) * 0.04;

  return [base[0] + latOffset, base[1] + lngOffset];
};
