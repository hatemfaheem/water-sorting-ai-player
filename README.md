<div align="center">
<br/>
<img src="docs/poster-water-sorting.png" alt="drawing" width="200"/>

# Water Sorting AI Player

<p>A fully automated AI player that plays water sorting puzzle game on mobile phones.</p>

<a href="https://youtu.be/qre8b8_nPd0?feature=shared">
    <img src="https://www.logo.wine/a/logo/YouTube/YouTube-Icon-Full-Color-Logo.wine.svg" width="50">
</a>

</div>

## The Game

https://play.google.com/store/apps/details?id=com.gma.water.sort.puzzle

Below are screenshots from the game for 2 different levels. 

<img src="docs/level_103_original.png" alt="drawing" width="200"/>
<img src="docs/level_104_original.png" alt="drawing" width="200"/>

## Overview

The AI player has 4 main steps:

1. Read level image from connected phone.
2. Scan the level image and represent in a data structure.
3. Solve the level given the level representation. Come up with a list of steps e.g. <Move tube X to tube Y>.
4. Given the solution steps, emulate touch events on the connected phone.

## Requirements

- `requirements.txt`
- Android Debug Bridge (change path in `/src/common/constants.py`)
