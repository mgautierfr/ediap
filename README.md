EDIAP
=====

EDIAP is for "Environnement de Développement intégré pour APrentissage".
This is french and it means "IDE for learning"

So what is EDIAP ?
------------------

EDIAP is a small ide written in python3/tkinter.
It is mainly inspired from the work of Bret Victor (http://worrydream.com/LearnableProgramming)
about how to create a program to learning programming.

Dependency
----------

EDIAP depends of picoparse.


First launch
------------

Just go :

$ ./ediap.py <inputfile.lsa>

If no input file is specified, EDIAP open first.lsa by default.

For now, there are two sample files : first.lsa and house.lsa


The UI
------

![A screenshot of the application](screenshot_house_annoted.png "A screenshot of the application")


1. This is were the code source is.
  - Read it,
  - edit it,
  - move the mouse's cursor on the tokens,
  - click/move the cursor on the tokens.
2. This is a slider to move from one step to another
3. This is where all the step are displayed. Each black circle is a step of the program. Move the mouse on a step to make it active.
4. This is where you get some information on what append during the active step.
5. Finaly, this is where you can see the current state (the of the active step). You can see the canvas, but also the hidden state of the canvas (the fill color), and the variables of the program.
    
