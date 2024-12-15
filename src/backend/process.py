import numpy as np
from PIL import Image
from mido import MidiFile
import json
import os
import time

# ========================= MUSIC INFORMATION RETRIEVAL ======================

# { Prekondisi: Path .mid benar, track dan channel terdefinisi }
# { Mengembalikan list pesan midi note_on/note_off pada track channel melodi
#   utama serta menambahkan absolute time setiap pesan }
def loadMidi(filePath):
    print("midifile")
    midi = MidiFile(filePath)
    print(midi)
    trackIdx, channelIdx = find_melody_track_and_channel_with_scoring(filePath)
    print("done dataidx")
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
    print(filePath)
    fileName = os.path.basename(filePath)
    print(fileName)
    print("pesan")
    pesan = loadMidi(filePath)
    print("tpb")
    tpb = getTicksPerBeat(filePath)
    print("windows")
    windows = makeWindows(pesan, tpb)
    print("atb")
    atb = extractATB(windows)
    print("rtb")
    rtb = extractRTB(windows)
    print("ftb")
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
    print("Cek midi say")
    for fileName in os.listdir(folderPath):
        if fileName.endswith(".mid"):
            midiFiles.append(fileName)
    
    print("Extract song say")
    dataset = []
    for fileName in midiFiles:
        song = extractFile("./datasetaudio/" + fileName)
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
    sim = simATB*0.05 + simRTB*0.475 + simFTB*0.475

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

# Fungsi pembantu mencari track dan channel melodi utama
def calculate_note_density(filtered_msgs):
    current_time = 0
    active_notes = 0
    active_time = 0
    total_time = 0

    messages = []
    for msg in filtered_msgs:
        current_time += msg.time
        messages.append((current_time, msg))

    messages.sort(key=lambda x: x[0])

    last_time = 0
    for timestamp, msg in messages:
        delta_time = timestamp - last_time
        if active_notes > 0:
            active_time += delta_time
        total_time += delta_time

        if msg.type == 'note_on' and msg.velocity > 0:
            active_notes += 1
        elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
            active_notes = max(active_notes - 1, 0)

        last_time = timestamp

    if total_time == 0:
        return 0
    return active_time / total_time

# { Prekondisi: filePath terdefinisi }
# { Mengembalikan data track, channel melodi utama }
def find_melody_track_and_channel_with_scoring(file_path, weights=None):
    midi = MidiFile(file_path)

    track_channel_info = {}

    if weights is None:
        weights = {
            'note_density': 0.20,
            'highest_note': 0.80,
            'note_on_count': 0.0  # Opsional
        }

    for track_idx, track in enumerate(midi.tracks):
        track_channel_info[track_idx] = {}
        for msg in track:
            if msg.type in ['note_on', 'note_off'] and hasattr(msg, 'channel'):
                channel = msg.channel
                if channel not in track_channel_info[track_idx]:
                    track_channel_info[track_idx][channel] = {
                        'highest_note': -1,
                        'note_density': 0.0,
                        'note_on_count': 0
                    }

                if msg.type == 'note_on' and msg.velocity > 0:
                    if msg.note > track_channel_info[track_idx][channel]['highest_note']:
                        track_channel_info[track_idx][channel]['highest_note'] = msg.note
                    track_channel_info[track_idx][channel]['note_on_count'] += 1

    for track_idx, track in enumerate(midi.tracks):
        for channel_idx in track_channel_info[track_idx]:
            filtered_msgs = [
                msg for msg in track 
                if hasattr(msg, 'channel') and msg.channel == channel_idx and msg.type in ['note_on', 'note_off']
            ]
            density = calculate_note_density(filtered_msgs)
            track_channel_info[track_idx][channel_idx]['note_density'] = density

    melody_track = None
    melody_channel = None
    max_score = -1

    for track_idx, channels in track_channel_info.items():
        for channel_idx, info in channels.items():
            score = 0.0
            score += weights.get('note_density', 0) * info['note_density']
            score += weights.get('highest_note', 0) * (info['highest_note'] / 127)
            score += weights.get('note_on_count', 0) * (info['note_on_count'] / max(info['note_on_count'] for c in channels.values()))

            if score > max_score:
                max_score = score
                melody_track = track_idx
                melody_channel = channel_idx

    if melody_track is not None and melody_channel is not None:
        return melody_track, melody_channel
    else:
        print("Unable to find main melody track and channel.")
        return None, None

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
    print("Mulai extract folder...")
    start = time.time()
    dataset = extractFolder(folderPath)
    end = time.time()
    extractTime = (end-start) * 10**3
    extractTime = round(extractTime, 2)

    print("Mulai extract file")
    song = extractFile(filePath)

    print("Mulai prediksi")
    start = time.time()
    prediction = predictSong(song, dataset)
    end = time.time()
    searchTime = (end-start) * 10**3
    searchTime = round(searchTime, 2)

    print("Mulai append")
    executionTime = extractTime + searchTime
    fileName = os.path.basename(filePath)
    result = []
    i = 0
    for info in prediction:
        if (info['sim'] > 90):
            print(f"{i+1}. {info['name']} {info['sim']}%")
            result.append(info)
            i += 1
    result.append({"execution": executionTime})
    if result:
        with open(resultPath, "w") as f:
            json.dump(result, f)
    else:
        print("apalah")

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
    i = 0
    for info in prediction:
        if (info['sim'] > 90):
            print(f"{i+1}. {info['name']} {info['sim']}%")
            result.append(info)
            i += 1
    result.append({"execution": executionTime})

    with open(resultPath, "w") as f:
        json.dump(result, f)

# ========================= MUSIC INFORMATION RETRIEVAL ======================

# # CONTOH MENJALANKAN PROGRAM
# filePath = "../../test/midi_dataset/sampleAPT3.mid"
# folderPath = "../../test/midi_dataset/"
# datasetPath = "../../test/adataset2.json"
# resultPath = "../../test/adresult1.json"

#makeDataset(folderPath, datasetPath)
# musicRetrieval(folderPath, filePath, resultPath)
#musicRetrievalDataset(datasetPath, filePath, resultPath)


# Image Processing and Loading
def preprocess_folder(folder_path, target_size=(100, 100)):
    image_vectors = []
    image_paths = []

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            filepath = os.path.join(folder_path, filename)
            image_paths.append(filepath)

            # Open image and process
            img = Image.open(filepath).convert('RGB')
            img_resized = img.resize(target_size)
            
            # Convert to grayscale
            img_array = np.array(img_resized)
            R, G, B = img_array[:, :, 0], img_array[:, :, 1], img_array[:, :, 2]
            grayscale = 0.2989 * R + 0.5870 * G + 0.1140 * B

            # Flatten and add to the list
            image_vectors.append(grayscale.flatten())

    return np.array(image_vectors), image_paths


def preprocess_file(file_path, target_size=(100, 100)):
    if not file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
        raise ValueError(f"Unsupported file type: {file_path}")

    # Open image and process
    img = Image.open(file_path).convert('RGB')
    img_resized = img.resize(target_size)
    
    # Convert to grayscale
    img_array = np.array(img_resized)
    R, G, B = img_array[:, :, 0], img_array[:, :, 1], img_array[:, :, 2]
    grayscale = 0.2989 * R + 0.5870 * G + 0.1140 * B

    # Flatten the image
    image_vector = grayscale.flatten()

    return image_vector

# Data Centering
def standardize_data(data):
    mean_vector = np.mean(data, axis=0)
    centered_data = data - mean_vector
    return centered_data, mean_vector

# PCA Computation Using SVD
def compute_pca(data, n_components):
    U, S, Vt = np.linalg.svd(data, full_matrices=False)
    eigenvectors = Vt[:n_components].T  # Top components
    projected_data = data @ eigenvectors
    return projected_data, eigenvectors, S[:n_components]

# Similarity Computation
def find_similar_images(query_image, dataset, eigenvectors, mean_vector, top_k=10):
    query_standardized = query_image - mean_vector
    query_projection = query_standardized @ eigenvectors


    distances = np.linalg.norm(dataset - query_projection, axis=1)
    d_min, d_max = np.min(distances), np.max(distances)

    if d_max != d_min:
        distances_percent = (distances - d_min) / (d_max - d_min) * 100
    else:
        distances_percent = np.zeros_like(distances)
    
    sim = 100 - distances_percent

    sorted_indices = np.argsort(distances)[:top_k]
    sorted_results = [(idx, sim[idx]) for idx in sorted_indices]

    return sorted_results


def ImageRetrieval(folder_path, filePath, resultPath, target_size=(100, 100), top_k=5, n_components=50):
    print("Mulai dataset")
    start = time.time()
    dataset_vectors, dataset_paths = preprocess_folder(folder_path, target_size=target_size)
    end = time.time()
    folder_preprocessing_time = round((end - start) * 10**3, 2)  # in milliseconds

    print("Standarisasi Dataset")
    standardized_data, mean_vector = standardize_data(dataset_vectors)

    print("SVD DATASET")
    projected_data, eigenvectors, _ = compute_pca(standardized_data, n_components=n_components)

    print("Proses Query")
    start = time.time()
    query_vector = preprocess_file(filePath, target_size=target_size)
    end = time.time()
    file_preprocessing_time = round((end - start) * 10**3, 2)  # in milliseconds

    print("Cari Similiar")
    start = time.time()
    similar_images = find_similar_images(query_vector, projected_data, eigenvectors, mean_vector, top_k=top_k)
    end = time.time()
    similarity_search_time = round((end - start) * 10**3, 2)  # in milliseconds
    print("Similar Images:", similar_images)

    total_execution_time = folder_preprocessing_time + file_preprocessing_time + similarity_search_time
    total_execution_time = round(total_execution_time, 2)

    query_file_name = os.path.basename(filePath)
    print("Isi Result")
    result = []  # Initialize an empty list

    for idx, sim in similar_images:
        sim = float(sim)
        if sim > 90:
            file_name = os.path.basename(dataset_paths[idx]) 
            result.append({
                "file": file_name,
                "sim": sim,
            })
    result.append({"execution": executionTime})


    with open(resultPath, "w") as f:
        json.dump(result, f)
    print("Selesai json")
