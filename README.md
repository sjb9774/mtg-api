# mtg-api

## A simple API for gathering information about Magic cards

This repo is meant to be a simple, portable, self-contained service for retrieving information
about Magic cards. The idea is that you can clone the repo to your own server and host an instance
of the database and API yourself so you're able to keep it as private or public as your like, which
gives you control over how much of a load you want on the database. This also provides a strict decoupling
between Magic information and the application that consumes it, leading to fewer opportunities to introduce
rigidness and unnecessary dependencies in your program.
