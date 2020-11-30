
import PySimpleGUI as sg
import os.path
from babyCrawler import *
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
from collections import Counter
from matplotlib import pyplot as plt
from matplotlib import dates
import datetime

def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg
    
def TextLabel(text): return sg.Text(text+':', justification='r', size=(5,1))
city = [[sg.Listbox(values=[], enable_events=True, size=(30,20),key='-CITY LIST-')]]

city_col = [[sg.Frame('Cities', city, pad=(0,0))]]
dist = [[sg.Listbox(values=[], enable_events=True, select_mode='multiple', size=(30,20),key='-DIST LIST-')]]
dist_col = [[sg.Frame('Districts', dist, pad=(0,0))]]
rest= [[sg.Listbox(values=[], enable_events=True, select_mode='multiple', size=(30,20),key='-REST LIST-')]]
rest_col = [[sg.Frame('Restaurants', rest, pad=(0,0))]]
button_col = [
                [sg.Button("Get Dishes")],
                [TextLabel('Min'),sg.Combo([0,1,2,3,4,5], size=(5, 6), default_value=0, key='min')],
                [TextLabel('Max'),sg.Combo([0,1,2,3,4,5], size=(5, 6), default_value=5, key='max')],
                [TextLabel('Date'),sg.Combo(['Day', 'Week', 'Month', 'Year'],default_value='Year', size=(5, 6), key='date')],
                [sg.Checkbox('Sort by A-Z',key='sort')],
                [sg.Button('Filter')],
                [sg.Button("Compare")],
                [sg.Checkbox('Filter Comparison',key='filtre')],
                [sg.Button("Analysis")],
                [sg.HorizontalSeparator()],
                [sg.Button('Update')],
                [sg.HorizontalSeparator()],
                
                [TextLabel('Thread'),sg.Combo([1,2,3,4,5,6,7,8], size=(5, 6), default_value=1, key='thread')],
                [sg.Checkbox('Continue crawl from selected',key='start')],
                [sg.Button('Crawl')]]


layout = [
    [sg.Column(city_col), sg.VSeperator(), sg.Column(dist_col), sg.VSeperator(), sg.Column(rest_col), sg.VSeperator(), sg.Column(button_col)],
    [sg.Column(
        [[sg.Table(values=[['                   ','                  ','                       ' ,'                   ']], 
                    headings=['Restaurant','Food Name','Price', 'Score'], max_col_width=500, background_color='lightblue',
                    auto_size_columns=True,
                    display_row_numbers=False,
                    justification='middle',
                    num_rows=20,
                    alternating_row_color='lightgreen',
                    key='TABLE',
                    size=(200,30),
                    text_color='black')]]),
        sg.VSeperator(),
        sg.Column([[sg.Table(values=[['          ','  ']], 
                    headings=['Restaurant\\District', 'Score'], max_col_width=500, background_color='lightblue',
                    auto_size_columns=True,
                    display_row_numbers=False,
                    justification='middle',
                    num_rows=20,
                    alternating_row_color='lightgreen',
                    key='Comparison',
                    size=(20,30),
                    
                    text_color='black'),]])
    ],

                    ]


window = sg.Window('Yemeksepeti Calc', layout)


file_list = os.listdir('./data')
b = True

while True:
    event, values = window.read()
    
    if event in (None, 'Exit'):
        break
    if b:
        window['-CITY LIST-'].update(file_list)
        b=not b
    if event == '-CITY LIST-':    
        try:
            cityfol = os.path.join('.\\data', values['-CITY LIST-'][0])
            
            dist_list = os.listdir(cityfol)
            
            window['-DIST LIST-'].update(dist_list)
            selected = (values['-CITY LIST-'][0],'','')

        except:
            pass       
    elif event == '-DIST LIST-':    
        try:
            selected = []
            rest_list = []
            for dists in range(len(values['-DIST LIST-'])):
                restfol = os.path.join('.\\data\\',values['-CITY LIST-'][0], values['-DIST LIST-'][dists])
                rest_list.extend(os.listdir(restfol))
                selected.append((values['-CITY LIST-'][0], values['-DIST LIST-'][dists],''))
            rest_list = list(dict.fromkeys(rest_list))
            
            window['-REST LIST-'].update(rest_list)
        except:
            pass  
 
    elif event == '-REST LIST-':    
        try:
            selected = []
            for dists in range(len(values['-DIST LIST-'])):
                restfol = os.path.join('.\\data\\',values['-CITY LIST-'][0], values['-DIST LIST-'][dists])
                rest_list = os.listdir(restfol)
                for rests in range(len(values['-REST LIST-'])):
                    if values['-REST LIST-'][rests] in rest_list:
                        selected.append((values['-CITY LIST-'][0], values['-DIST LIST-'][dists],values['-REST LIST-'][rests]))
        except:
            pass  
 
    elif event == 'Get Dishes' or event == 'Filter':
        try:
            table = pd.DataFrame()
            for city, dist, rest in selected:
                if event != 'Filter':
                    table = pd.concat((table, localDishesnComments(city,dist,rest)),axis=0)
                else:
                    table = pd.concat((table, localDishesnComments(city,dist,rest, min=window['min'].get(), max=window['max'].get(), date=window['date'].get(), sort_rest=window['sort'].get())),axis=0)
            
            table.sort_values(by='food_score',inplace=True, ascending=False)
            window['TABLE'].update(values=table.values.tolist())
        except:
            pass  
    
    elif event == 'Compare':
        try:
            comparison = []

            table = pd.DataFrame()
            for city, dist, rest in selected:
                if not window['filtre'].get():
                    if rest != '':
                        tmp = localDishesnComments(city,dist,rest)
                        mean_score = np.mean(tmp['food_score'].to_numpy())
                        mean_score = np.around(mean_score,2)
                        comparison.append([rest,mean_score])
                    else:
                        tmp = localDishesnComments(city,dist,rest)
                        mean_score = np.mean(tmp['food_score'].to_numpy())
                        mean_score = np.around(mean_score,2)
                        comparison.append([dist,mean_score])
                else:
                    if window['min'].get() >= window['max'].get():
                        sg.popup_error('Min can\'t be greater than max')
                        continue
                    if rest != '':
                        tmp = localDishesnComments(city,dist,rest, min=window['min'].get(), max=window['max'].get(), date=window['date'].get(), sort_rest=window['sort'].get())
                        mean_score = np.mean(tmp['food_score'].to_numpy())
                        mean_score = np.around(mean_score,2)
                        comparison.append([rest,mean_score])
                    else:
                        tmp = localDishesnComments(city,dist,rest, min=window['min'].get(), max=window['max'].get(), date=window['date'].get(), sort_rest=window['sort'].get())
                        mean_score = np.mean(tmp['food_score'].to_numpy())
                        mean_score = np.around(mean_score,2)
                        comparison.append([dist,mean_score])
            comparison.sort(key=lambda x:x[1])
            window['Comparison'].update(values=comparison)
        except:
            pass  

    elif event == 'Update':
        try:
            updateRestaurant(values['-CITY LIST-'][0], values['-DIST LIST-'][0],values['-REST LIST-'][0])
        except:
            pass

    elif event == 'Analysis':
        try:
            aa = do_analysis(values['-CITY LIST-'][0], values['-DIST LIST-'][0],values['-REST LIST-'][0])
            popi = aa.Food.mode()
            # print(popi[0])
            t = aa[aa['Food']==popi[0]]['Ordered on']
            c = Counter(t)
            d = []
            y1 = []
            for xs in c:
                d.append(xs)
                y1.append(c[xs])
            s = np.asarray(d)
            y1 = np.asarray(y1)
            fds = []
            for ss in s:
                fds.append(dates.date2num(datetime.datetime.fromtimestamp(ss)))
            
            
            hfmt = dates.DateFormatter('%Y-%m-%d')
            fig = matplotlib.figure.Figure(figsize=(5, 4), dpi=100)
            ax = fig.add_subplot(111)
            ax.xaxis.set_major_locator(dates.DayLocator(interval=10))
            ax.xaxis.set_major_formatter(hfmt)
            matplotlib.use('TkAgg')
            ax.locator_params(axis='x', nbins=5)
            ax.plot(fds,y1)
            plt.xticks(rotation=45)
            layout2 = [[sg.Text(('Analysis on: '+popi[0]))],
                    [sg.Canvas(key='-CANVAS-')]]

            # create the form and show it without the plot
            window2 = sg.Window('Analysis Graph', layout2, location=(0,0), finalize=True, element_justification='center', font='Helvetica 12')

            # add the plot to the window
            draw_figure(window2['-CANVAS-'].TKCanvas, fig)

        except:
            pass
        
    elif event == 'Crawl':
        y = sg.popup_yes_no('This is going to render the gui unusable. \n\t Continue?')
        if y == 'Yes':
            if window['thread'].get() > 1:
                y = sg.popup_yes_no('Yemeksepeti bans concurrent crawling, consider switching to singlethread crawling.')
                if y == 'No':
                    if window['start'].get():
                        multithread(window['thread'].get(), file_list.index(values['-CITY LIST-'][0]))
                    else:
                        multithread(window['thread'].get())
            else:
                if window['start'].get():
                    multithread(window['thread'].get(), file_list.index(values['-CITY LIST-'][0]))
                else:
                    multithread(window['thread'].get())

window.close()