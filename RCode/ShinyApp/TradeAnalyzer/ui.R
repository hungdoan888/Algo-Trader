#
# This is the user-interface definition of a Shiny web application. You can
# run the application by clicking 'Run App' above.
#
# Find out more about building applications with Shiny here:
#
#    http://shiny.rstudio.com/
#

library(shiny)

shinyUI(fluidPage(navlistPanel(
    tabPanel("test1", "This is test page 1"),
    tabPanel("test2", "This is test page 2")
)))
