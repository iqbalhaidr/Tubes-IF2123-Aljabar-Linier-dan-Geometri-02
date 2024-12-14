import numpy as np
#from PIL import Image
from mido import MidiFile
import json
import os
import time

# ========================= MUSIC INFORMATION RETRIEVAL ======================

# { Prekondisi: Path .mid benar, track dan channel terdefinisi }
# { Mengembalikan list pesan midi note_on/note_off pada track channel melodi
#   utama serta menambahkan absolute time setiap pesan }
def loadMidi(filePath):
    midi = MidiFile(filePath)

    dataIdx = findTrackChannel(filePath)
    trackIdx = dataIdx['track']
    channelIdx = dataIdx['channel']
    
    track = midi.tracks[trackIdx]
    pesan = []
    absoluteTime = 0
    isFirst = True
    for msg in track:
        if hasattr(msg, 'channel') and msg.channel == channelIdx and msg.type in ['note_on', 'note_off']:
            if isFirst: # Memastikan absoluteTime pesan pertama 0
                msg.time = 0
                isFirst = False
            absoluteTime += msg.time
            pesan.append((msg, absoluteTime))

    return pesan

# { Prekondisi: Path .mid benar }
# { Mengembalikan tick per beat dari file midi }
def getTicksPerBeat(filePath):
    midi = MidiFile(filePath)
    return midi.ticks_per_beat

# { Mengembalikan list dengan tidak ada elemen yang sama berurutan 
#   [1, 1, 2, 3, 3, 4, 3, 1] -> [1, 2, 3, 4, 3, 1] }
def removeSeqDupes(listO):
    return [listO[i] for i in range(len(listO)) if i == 0 or listO[i] != listO[i - 1]]

# { Prekondisi: pesan adalah list pesan midi + absolute time, mungkin kosong, 
#   windowSizeBeats, slideSizeBeats, tickPerBeat terdefinisi dalam beat }
# { Mengembalikan list of window berisi pitch sesuai parameter }
# TODO: [OPTIMASI] List kosong tidak perlu diproses
def makeWindows(pesan, ticksPerBeat, windowSizeBeats=30, slideSizeBeats=6):
    windowSizeTicks = windowSizeBeats * ticksPerBeat
    slideSizeTicks = slideSizeBeats * ticksPerBeat
    windows = []
    startTime = 0

    while startTime < pesan[-1][1]: # Akses absoluteTime maksimum
        notePool = []
        window = []
        noteCtr = 0
        for msg, absoluteTime in pesan:
            if (startTime <= absoluteTime < startTime + windowSizeTicks
                and msg.type  in ['note_on', 'note_off']):
                if msg.velocity > 0: # STARTNOTE
                    if msg.time == 0 or len(notePool) == 0:
                        notePool.append(msg.note)
                    else: 
                        highestPitchOnInterval = max(notePool)
                        window.append(highestPitchOnInterval)
                        noteCtr += 1
                        notePool.append(msg.note)
                else: # ENDNOTE
                    if len(notePool) == 0 or msg.note not in notePool:
                        continue
                    elif msg.time == 0:
                        notePool.remove(msg.note)
                    else:
                        highestPitchOnInterval = max(notePool)
                        window.append(highestPitchOnInterval)
                        noteCtr += 1
                        notePool.remove(msg.note)
            elif absoluteTime >= startTime + windowSizeTicks:
                break
        
        window = removeSeqDupes(window)
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

# { Prekondisi: filePath terdefinisi benar .mid }
# { Mengembalikan dict <nama, fiturATB, fiturRTB, fiturFTB> sebuah file/lagu }
# TODO: [OPTIMASI] MULTITHREADING
def extractFile(filePath):
    fileName = os.path.basename(filePath)

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

# { Prekondisi: folderPath terdefinisi benar .mid }
# { Mengembalikan list of dict <nama, fiturATB, fiturRTB, fiturFTB> sebuah 
#   file/lagu }
def extractFolder(folderPath):
    midiFiles = []
    for fileName in os.listdir(folderPath):
        if fileName.endswith(".mid"):
            midiFiles.append(fileName)
    
    dataset = []
    for fileName in midiFiles:
        song = extractFile(folderPath + fileName)
        dataset.append(song)

    return dataset

# { Prekondisi: vec1 dan vec2 adalah vector/representasi numerik histogram }
# { Mengembalikan nilai kesamaan antara kedua vektor }
def cosineSimilarity(vec1, vec2):
    dotProduct = np.dot(vec1, vec2)
    normVec1 = np.linalg.norm(vec1)
    normVec2 = np.linalg.norm(vec2)
    return dotProduct / (normVec1 * normVec2) if normVec1 > 0 and normVec2 > 0 else 0.0

# { Prekondisi: querySong, datasetSong adalah dict fitur file/lagu }
# { Mengembalikan nilai similaritas dari cosineSimilarity() }
# TODO: [OPTIMASI] Pencarian Similaritas
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

    # Rumus pembobotan yang optimal setelah dilakukan eksperimen
    sim = simATB*0.05 + simRTB*0.55 + simFTB*0.40

    return sim

# { Prekondisi: querySong adalah <nama, fiturATB, fiturRTB, fiturFTB> }
# { Mengembalikan list prediksi/similaritas querySong dengan semua lagu pada
#   dataset terurut menurun }
def predictSong(querySong, dataset):
    prediction = []
    for song in dataset:
        sim = float(computeSimilarity(querySong, song))
        sim *= 100
        sim = round(sim, 2)
        prediction.append({'name': song['name'], 'sim': sim})
    return sorted(prediction, key=lambda x: x['sim'], reverse=True)

# { I.S. dataset terdefinisi }
# { F.S. Menyimpan dataset pada ./<datasetPath> (default) dalam bentuk dict }
def saveDataset(dataset, datasetPath="dataset.json"):
    convertedDataset = []
    
    for song in dataset:
        name = song['name']
        atb = song['atb']
        rtb = song['rtb']
        ftb = song['ftb']
        
        convertedATB = [window.tolist() for window in atb]
        convertedRTB = [window.tolist() for window in rtb]
        convertedFTB = [window.tolist() for window in ftb]
        
        convertedSong = {
            'name': name,
            'atb': convertedATB,
            'rtb': convertedRTB,
            'ftb': convertedFTB
        }
        convertedDataset.append(convertedSong)

    with open(datasetPath, "w") as f:
        json.dump(convertedDataset, f)

# { I.S. Prekondisi: filePath terdefinisi }
# { F.S. Memasukkan data pada <datasetPath> ke dalam program dalam bentuk list of dict }
def loadDataset(datasetPath):
    with open(datasetPath, "r") as f:
        data = json.load(f)
    
    convertedDataset = []
    
    for song in data:
        name = song['name']
        atb = [np.array(window) for window in song['atb']]
        rtb = [np.array(window) for window in song['rtb']]
        ftb = [np.array(window) for window in song['ftb']]
        
        convertedSong = {
            'name': name,
            'atb': atb,
            'rtb': rtb,
            'ftb': ftb
        }
        convertedDataset.append(convertedSong)
    
    return convertedDataset

# { Prekondisi: filePath terdefinisi }
# { Mengembalikan dict berisi data track, channel melodi utama }
def findTrackChannel(filePath):
    midi = MidiFile(filePath)
    trackInfo = []

    for i, track in enumerate(midi.tracks):
        channelInfo = {}
        notes = []

        for msg in track:
            if msg.type == 'note_on' and msg.velocity > 0:
                notes.append({
                    'channel': msg.channel,
                    'pitch': msg.note,
                    'velocity': msg.velocity
                })

        channels = {}
        for note in notes:
            ch = note['channel']
            if ch not in channels:
                channels[ch] = {
                    'notes': []
                }
            channels[ch]['notes'].append(note)

        for ch, info in channels.items():
            pitches = [n['pitch'] for n in info['notes']]
            if not pitches:
                continue
            pitchRange = max(pitches) - min(pitches)
            totalNotes = len(pitches)
            avgVelocity = sum(n['velocity'] for n in info['notes']) / totalNotes

            # Pen-skor-an sederhana
            score = pitchRange + totalNotes * 0.1 + avgVelocity * 0.01

            trackInfo.append({
                'track': i,
                'channel': ch,
                'score': score
            })

    # Filter hanya channel 0 dan track terdefinisi
    filteredInfo = [info for info in trackInfo if info['channel'] == 0 and info['track'] is not None]

    # Jika kosong kembalikan track, channel manapun dengan skor tertinggi
    if not filteredInfo:
        return max(trackInfo, key=lambda x: x['score'])

    # Pilih track, channel skor tertinggi setelah difilter
    mainMelody = max(filteredInfo, key=lambda x: x['score'])
    return mainMelody

# { I.S. folderPath terdefinisi berisi .mid
#   F.S. Mengekstraksi fitur dari setiap file.mid pada folderPath
#        lalu menyimpannya di datasetPath dalam bentuk .json}
def makeDataset(folderPath, datasetPath):
    dataset = extractFolder(folderPath)
    saveDataset(dataset, datasetPath)

# ===============================================================================

# { I.S. folderPath, filePath terdefinisi berupa .mid }
# { F.S. Menjalankan fungsi music retrieval dengan dataset berupa semua file 
#        .mid pada folderPath dan filePath sebagai query nya. 10 pencocokan teratas 
#        akan di print serta disimpan dalam file resultPath berbentuk 
#        list of dict <'name', 'sim'> dan index ke 10 disimpan execution time ms, 
#        index ke 11 berisi nama file query }
# NOTE: INI MERUPAKAN FUNGSI GABUNGAN MENJALANKAN MUSIC RETRIEVAL
def musicRetrieval(folderPath, filePath, resultPath):
    start = time.time()
    dataset = extractFolder(folderPath)
    end = time.time()
    extractTime = (end-start) * 10**3
    extractTime = round(extractTime, 2)

    song = extractFile(filePath)

    start = time.time()
    prediction = predictSong(song, dataset)
    end = time.time()
    searchTime = (end-start) * 10**3
    searchTime = round(searchTime, 2)

    executionTime = extractTime + searchTime
    fileName = os.path.basename(filePath)
    result = []
    print(f"\nQuery Song: {fileName}\n")
    for i in range (10):
        print(f"{i+1}. {prediction[i]['name']} {prediction[i]['sim']}%")
        result.append(prediction[i])
    print(f"\nExtract Time: {extractTime} ms")
    print(f"Search Time: {searchTime} ms")
    print(f"Total Execution Time: {executionTime} ms")
    result.append(executionTime)
    result.append(fileName)

    with open(resultPath, "w") as f:
        json.dump(result, f)

# { I.S. datasetPath, filePath terdefinisi. file dataset dibuat dari 
#        fungsi makeDataset 
#   F.S. SAMA SEPERTI musicRetrieval namun dengan dataset yang menyimpan 
#        kumpulan informasi fitur dari lagu sehingga tidak perlu lagi menghitungnya
#        diawal }
def musicRetrievalDataset(datasetPath, filePath, resultPath):
    start = time.time()
    dataset = loadDataset(datasetPath)
    end = time.time()
    loadTime = (end-start) * 10**3
    loadTime = round(loadTime, 2)

    song = extractFile(filePath)

    start = time.time()
    prediction = predictSong(song, dataset)
    end = time.time()
    searchTime = (end-start) * 10**3
    searchTime = round(searchTime, 2)

    executionTime = loadTime + searchTime
    fileName = os.path.basename(filePath)
    result = []
    print(f"\nQuery Song: {fileName}\n")
    for i in range (10):
        print(f"{i+1}. {prediction[i]['name']} {prediction[i]['sim']}%")
        result.append(prediction[i])
    print(f"\nLoad Time: {loadTime} ms")
    print(f"Search Time: {searchTime} ms")
    print(f"Total Execution Time: {executionTime} ms")
    result.append(executionTime)
    result.append(fileName)

    with open(resultPath, "w") as f:
        json.dump(result, f)

# ========================= MUSIC INFORMATION RETRIEVAL ======================

# CONTOH MENJALANKAN PROGRAM
filePath = "../../test/midi_dataset/sampleAPT3.mid"
folderPath = "../../test/midi_dataset/"
datasetPath = "../../test/adataset2.json"
resultPath = "../../test/adresult1.json"

#makeDataset(folderPath, datasetPath)
musicRetrieval(folderPath, filePath, resultPath)
#musicRetrievalDataset(datasetPath, filePath, resultPath)
