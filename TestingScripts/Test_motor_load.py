from TryPy.LoadData import LoadMotorFile
import matplotlib.pyplot as plt

FileIn = '../Data/2304Motor/2304Motor04.csv'

data = LoadMotorFile(FileIn)

fig, ax = plt.subplots()

#Calc velocity

# data['Velocity2'] = data.Position.diff()/1000 / data.Time.diff()
# data['Accelation'] = data.Velocity2.diff() / data.Time.diff()

ax.plot(data['Time'], data['Position'])
axv = plt.twinx(ax)
axv.plot(data['Time'], data['Velocity'], 'g')
axa = plt.twinx(ax)
axa.plot(data['Time'], data['Acceleration'], 'r')

plt.show()