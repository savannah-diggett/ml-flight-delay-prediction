# Flight Delay Prediction Dataset

## Overview
**Source**: [US BTS TranStats On-Time Performance (2018-2022) Dataset](https://www.transtats.bts.gov/DL_SelectFields.aspx?gnoyr_VQ=FGJ&QO_fu146_anzr=b0-gvzr)
**Scope**: Flights arriving at ORD, JFK, ATL hub airports
**Target**: Multiclass arrival delay severity classification

## Schema

| Column | Type | Description |
|--------|------|-------------|
| `carrier_id` | `int` | DOT airline ID (e.g., 19393 = Southwest Airlines) |
| `origin` | `string` | Origin airport code (ORD/JFK/ATL focus airports) |
| `dest` | `string` | Destination airport code |
| `dep_hour` | `int` | Scheduled departure hour (0-23) |
| `year` | `int` | Flight year (2018-2023) |
| `day_of_week` | `int` | Day of week (1=Monday, 7=Sunday) |
| `month` | `int` | Flight month (1-12) |
| `distance` | `double` | Great circle distance between airports (miles) |
| `distance_group` | `int` | Distance bucket: 0=Short(≤500mi), 1=Medium(≤1000), 2=Long(≤2000), 3=XLong |
| `arr_delay` | `double` | Actual arrival delay (minutes, negative = early) |
| `delay_carrier` | `int` | Binary: 1 if carrier caused delay |
| `delay_weather` | `int` | Binary: 1 if weather caused delay |
| `delay_nas` | `int` | Binary: 1 if National Airspace System congestion |
| `delay_security` | `int` | Binary: 1 if security screening delay |
| `delay_late_aircraft` | `int` | Binary: 1 if late arriving aircraft |
| `delay_none` | `int` | Binary: 1 if no delay causes recorded (on-time/early) |
| **`delay_class`** | **`int`** | **Target**: 0=No(≤0min), 1=Minor(≤60min), 2=Major(≤120min), 3=Severe(>120min) |
