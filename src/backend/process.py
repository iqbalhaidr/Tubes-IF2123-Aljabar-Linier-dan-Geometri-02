import numpy as np
#from PIL import Image
from mido import MidiFile
import json
import os
import time

# { Prekondisi: Path .mid benar, track dan channel terdefinisi }
# { Mengembalikan list pesan midi note_on/note_off Track X Channel Y, 
#   menambahkan absolute time pada tiap pesan }
# TODO: [BUG ASAP] jika track/channel tidak sesuai asumsi track=1, channel=0
def loadMidi(filePath, trackIdx=1, channelIdx=0):
    midi = MidiFile(filePath)

    # ERROR CHECK (DELETE SOON)
    if trackIdx >= len(midi.tracks):
        trackIdx = 0
        #raise IndexError(f"Track index {trackIdx} tidak ditemukan. "
                        #f"File hanya memiliki {len(midi.tracks)} track.")
    
    track = midi.tracks[trackIdx]
    pesan = []
    absoluteTime = 0
    isFirst = True
    for msg in track:
        if hasattr(msg, 'channel') and msg.channel == channelIdx and msg.type in ['note_on', 'note_off']:
            if isFirst: # Memastikan relative time note pertama = 0
                msg.time = 0
                isFirst = False
            absoluteTime += msg.time
            pesan.append((msg, absoluteTime))
    """
    if len(pesan) < 1:
        print(len(midi.tracks))
        print("INFINITE LOOP AJG")
        loadMidi(filePath, 0, 1)
    """
    #print(len(pesan))
    return pesan

# { Prekondisi: Path .mid benar }
# { Mengembalikan tick per beat dari file midi }
def getTicksPerBeat(filePath):
    midi = MidiFile(filePath)
    return midi.ticks_per_beat

# { Prekondisi: pesan adalah list pesan midi + absolute time, mungkin kosong, 
#   windowSizeBeats, slideSizeBeats, tickPerBeat terdefinisi dalam beat }
# { Mengembalikan list of window berisi pitch sesuai parameter }
# CATATAN: if ctr > 8: itu asumsi tiap note ukuran paling panjang = 4 beat -> 30/4 = 7,5
#          jadi kalo < 7,5 diasumsikan kebanyakan gaada suara
#   TODO: [AKURASI] idealnya relative time dan absolute time itu dipotong/disesuaikan
#   TODO: [OPTIMASI] jika window kosong jangan di append
def makeWindows(pesan, ticksPerBeat, windowSizeBeats=30, slideSizeBeats=6):
    windowSizeTicks = windowSizeBeats * ticksPerBeat
    slideSizeTicks = slideSizeBeats * ticksPerBeat
    windows = []
    startTime = 0

    while startTime < pesan[-1][1]: # Akses absoluteTime maksimum
        window = []
        ctr = 0
        for msg, absoluteTime in pesan:
            if (startTime <= absoluteTime < startTime + windowSizeTicks
                and msg.type == 'note_on' and msg.velocity > 0):
                window.append(msg.note)
                ctr += 1
            elif absoluteTime >= startTime + windowSizeTicks:
                break
        if ctr > 8:
            windows.append(window)
        startTime += slideSizeTicks

    return windows

# { Prekondisi: windows terdefinisi list of window sesuai parameter }
# { Mengembalikan list of histogram fitur ATB yang sudah dinormalisasi }
def extractATB(windows):
    features = []
    numBins = 128
    binEdges = np.linspace(0, 127, numBins + 1)

    for window in windows:
        histogram, _ = np.histogram(window, bins=binEdges)
        totalCount = np.sum(histogram)
        normalizedHistogram = histogram / totalCount if totalCount > 0 else histogram
        features.append(normalizedHistogram)
    
    return features

# { Prekondisi: windows terdefinisi list of window sesuai parameter }
# { Mengembalikan list of histogram fitur RTB yang sudah dinormalisasi }
def extractRTB(windows):
    features = []
    numBins = 255
    binEdges = np.linspace(-127, 127, numBins + 1)

    for window in windows:
        intervals = [window[i+1] - window[i] for i in range(len(window) - 1)]
        histogram, _ = np.histogram(intervals, bins=binEdges)
        totalCount = np.sum(histogram)
        normalizedHistogram = histogram / totalCount if totalCount > 0 else histogram
        features.append(normalizedHistogram)
    
    return features

# { Prekondisi: windows terdefinisi list of window sesuai parameter }
# { Mengembalikan list of histogram fitur FTB yang sudah dinormalisasi }
def extractFTB(windows):
    features = []
    numBins = 255
    binEdges = np.linspace(-127, 127, numBins + 1)

    for window in windows:
        if not window:
            features.append(np.zeros(numBins))
            continue

        firstPitch = window[0]
        relativePitches = [pitch - firstPitch for pitch in window]
        histogram, _ = np.histogram(relativePitches, bins=binEdges)
        totalCount = np.sum(histogram)
        normalizedHistogram = histogram / totalCount if totalCount > 0 else histogram
        features.append(normalizedHistogram)
    
    return features

def extractFile(fileName):
    filePath = "../../test/" + fileName

    pesan = loadMidi(filePath)
    tpb = getTicksPerBeat(filePath)
    windows = makeWindows(pesan, tpb)
    atb = extractATB(windows)
    rtb = extractRTB(windows)
    ftb = extractFTB(windows)
    return {
        'name': fileName,
        'atb': atb,
        'ftb': ftb,
        'rtb': rtb
    }

def extractFolder(folderPath):
    midiFiles = []
    for fileName in os.listdir(folderPath):
        if fileName.endswith(".mid"):  # Filter file MIDI
            midiFiles.append(fileName)
    
    dataset = []
    for fileName in midiFiles:
        song = extractFile(fileName)
        dataset.append(song)
    
    print("LOAD DATABASE DONE!")
    
    return dataset

def cosineSimilarity(vec1, vec2):
    dotProduct = np.dot(vec1, vec2)
    normVec1 = np.linalg.norm(vec1)
    normVec2 = np.linalg.norm(vec2)
    return dotProduct / (normVec1 * normVec2) if normVec1 > 0 and normVec2 > 0 else 0.0

def computeSimilarity(querySong, datasetSong):
    windowsSimATB = []
    for queryATB in querySong['atb']:
        currentWindowSim = []
        for datasetATB in datasetSong['atb']:
            sim = cosineSimilarity(queryATB, datasetATB)
            currentWindowSim.append(sim)
        maxSim = max(currentWindowSim)
        windowsSimATB.append(maxSim)
    simATB = sum(windowsSimATB) / len(windowsSimATB)

    windowsSimRTB = []
    for queryRTB in querySong['rtb']:
        currentWindowSim = []
        for datasetRTB in datasetSong['rtb']:
            sim = cosineSimilarity(queryRTB, datasetRTB)
            currentWindowSim.append(sim)
        maxSim = max(currentWindowSim)
        windowsSimRTB.append(maxSim)
    simRTB = sum(windowsSimRTB) / len(windowsSimRTB)

    windowsSimFTB = []
    for queryFTB in querySong['ftb']:
        currentWindowSim = []
        for datasetFTB in datasetSong['ftb']:
            sim = cosineSimilarity(queryFTB, datasetFTB)
            currentWindowSim.append(sim)
        maxSim = max(currentWindowSim)
        windowsSimFTB.append(maxSim)
    simFTB = sum(windowsSimFTB) / len(windowsSimFTB)

    return (simATB + simRTB + simFTB) / 3

def predictSong(querySong, dataset):
    prediction = []
    for song in dataset:
        sim = float(computeSimilarity(querySong, song))
        sim *= 100
        sim = round(sim, 2)
        prediction.append({'name': song['name'], 'sim': sim})
    return sorted(prediction, key=lambda x: x['sim'], reverse=True)

def saveDataset(dataset, outputFile="dataset.json"):

    with open(outputFile, "w") as f:
        json.dump(dataset, f)

def loadDataset(inputFile="dataset.json"):
    with open(inputFile, "r") as f:
        dataset = json.load(f)
    return dataset




#DEBUG
def printTrack(filePath, track):
    midi = MidiFile(filePath)
    tracks = midi.tracks
    count = 0
    for msg in tracks[track]:
        #if hasattr(msg, 'channel') and msg.channel == 0 and msg.type in ['note_on', 'note_off']:
            print(msg)
            count += 1
    print(f"count: {count}")

def infoTrack(filePath):
    midi = MidiFile(filePath)
    tracks = midi.tracks
    print(filePath)
    for idx, trac in enumerate(tracks):
        print(f"Panjang Track {idx} = {len(trac)}")

def infoFile(fileName):
    print("file:", type(fileName))
    print("fileName:", fileName['name'])
    print("name:", type(fileName['name']))

    print("\nlen atb:", len(fileName['atb']))
    print("atbWindows:", type(fileName['atb']))
    print("atbWindow:", type(fileName['atb'][0]))
    print("atbVector:", type(fileName['atb'][0][0]))

    print("\nlen rtb:", len(fileName['rtb']))
    print("rtbWindows:", type(fileName['rtb']))
    print("rtbWindow:", type(fileName['rtb'][0]))
    print("rtbVector:", type(fileName['rtb'][0][0]))

    print("\nlen ftb:", len(fileName['ftb']))
    print("ftbWindows:", type(fileName['ftb']))
    print("ftbWindow:", type(fileName['ftb'][0]))
    print("ftbVector:", type(fileName['ftb'][0][0]))

def infoDataset(dataset):
    print("dataset len:", len(dataset))
    print("dataset type:", type(dataset))
    print("\n[===============================================]\n")
    for song in dataset:
        infoFile(song)
        print("\n[===============================================]\n")

def infoPrediction(prediction):
    for song in prediction:
        print("name:", song['name'])
        print("nametype:", type(song['name']))
        print("sim:", song['sim'])
        print("simtype:", type(song['sim']))


# main()
start = time.time()
# ==========================================================


#pathFile = "../../test/PROBsample4.mid"
#printTrack(pathFile, 0)
#infoTrack(pathFile)
#fileName = "bsbiw.mid"
#folderPath = "../../test/"
#dataset = extractFolder(folderPath)
#end = time.time()
#prediction = predictSong(dataset[0], dataset)
#print(prediction)
#infoPrediction(prediction)
#infoDataset(dataset)
# record end time


# ==========================================================

end = time.time()
print("The time of execution of above program is :",
      (end-start) * 10**3, "ms")
