from models.note import Note, Notes, ScaleNotes, Octave
from models.frequency_range import FrequencyRange
from audio import play, play_multiple
from time import sleep
import numpy as np

class Progression(object):
  blueprints = {}

  def __init__(self, key, progression_type='major'):
    self.key = key
    self.root = Note(key)
    self.note_order = self.blueprints[progression_type.lower()]
    self.title = progression_type.replace('-',' ').title()
    self.name = "%s %s" % (self.key, self.title)
    self.notes = []
    self.overtone_range_cache = {}
    for scale_number in self.note_order:
      halfsteps = ScaleNotes.index(scale_number)
      note = self.root + halfsteps
      self.notes.append(note)

  def get_frequencies(self):
    return list(map(lambda n: n.frequency, self.notes))

  def get_scale_number(self, note):
    return Note.get_scale_number(self.root, note)

  def overtone_ranges(self, n, accuracy):
    key = "%d%f" % (n, accuracy)
    if not key in self.overtone_range_cache:
      ranges = []
      for note in self.notes:
        low_note = Note(note)
        low_note.set_octave(2)
        ranges += low_note.overtone_ranges(n, accuracy)
      
      self.overtone_range_cache[key] = FrequencyRange.simplify(ranges)

    return self.overtone_range_cache[key]

  def contains(self, frequency, n, accuracy):
    ranges = self.overtone_ranges(n, accuracy)
    return any(map(lambda r: r.contains(frequency), ranges))

  @classmethod
  def guess(cls, notes):
    notes = list(map(Note, notes))
    for root in notes:
      progression = list(map(lambda note: Note.get_scale_number(root, note), notes))
      progression = sorted(set(progression))
      for chord_type, chord_progression in cls.blueprints.items():
        if chord_progression == progression:
          return str(root.note) + ' ' + chord_type.title()

    return 'Unkown Chord'

  @classmethod
  def all(cls):
    all_progressions = []
    for progression_type in cls.blueprints:
      for note in Notes:
        all_progressions.append(cls(note, progression_type))
    
    return all_progressions
  
  def __str__(self):
    return ','.join(map(lambda n: n.note, self.notes))

class Chord(Progression):
  blueprints = {
    'major'          : ['1','3', '5'],
    'minor'          : ['1','3b', '5'],
    # 'sus4'           : ['1','4','5'],   
    # 'sus2'           : ['1','2','5'],
    # 'diminished'     : ['1', '3b', '5b'],
    # 'major7'         : ['1', '3', '5', '7'],
    # 'minor7'         : ['1', '3b', '5', '7b'],
    '7'              : ['1', '3', '5', '7b'],
    # '7sus4'          : ['1', '4','5', '7b'],
    # '7sus2'          : ['1','2','5', '7b'],
    # 'diminished7'    : ['1', '3b', '5b', '6'],
  }

  def play(self, time=1, delay=0):
    play_multiple(self.get_frequencies(), time=time, delay=delay)

class Scale(Progression):
  blueprints = {
    'major'              : ['1', '2', '3', '4', '5', '6', '7','8'],
    'minor'              : ['1', '2', '3b', '4', '5', '6b', '7b','8'],
    'major-pentatonic'   : ['1', '2', '3', '5', '6','8'],
    'minor-pentatonic'   : ['1', '3b', '4', '5', '7b','8'],
    'major-blues'        : ['1', '3b', '4', '5b', '5', '7b','8'],
    'minor-blues'        : ['1', '2', '3b', '3', '5', '6','8'],
    'Harmonic'           : ['1', '2', '3b', '4', '5', '6', '7b','8'],
  }

  def play(self, time=1, octaves=1, reverse=False):
    self.root.play(time=time)

    for octave in range(0, octaves):
      for index, note in enumerate(self.notes):
        if (index > 0):
          note_on_octave = note + (octave * Octave)
          note_on_octave.play(time=time)
          sleep(time / 2)

    if reverse:
      reverse_octaves = list(range(0, octaves))
      reverse_octaves.reverse()
      reverse_notes = self.notes.copy()
      reverse_notes.reverse()
      for octave in reverse_octaves:
        for index, note in enumerate(reverse_notes):
          if (index > 0):
            note_on_octave = note + (octave * Octave)
            note_on_octave.play(time=time)
            sleep(time / 2)

class Arpeggio(Scale):
  blueprints = {
    'major'          : ['1', '3', '5', '8'],
    'minor'          : ['1','3b', '5', '8'],
  }
