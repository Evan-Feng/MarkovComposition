from __future__ import print_function
from music21 import *
import prettytable
from collections import defaultdict
import argparse
from random import choice
import json
from fractions import Fraction


def generate_stream(note_list, play=False):
    '''
    Given a note list in the form of
    List[List[str, int/float], List[str, int/float], ...]
    [[<step>, <quaterlength>], [<step>, <quaterlength>], ...]
    generate a music21.stream.Score object and play soundtrack of it if
    "play" is specified as True, or display it in a MusicXML reader
    software suck as MuseScore by defualt. Returns nothing.
    '''
    pitch_stream = stream.Part()

    for step, qlen in note_list:
        if step == 'R':
            n = note.Rest(quarterLength=qlen)
        else:
            n = note.Note(step, quarterLength=qlen)
        pitch_stream.append(n)

    pitch_stream.makeMeasures(inPlace=True)
    if play:
        pitch_stream.show('midi')
    else:
        pitch_stream.show()


def calculate_markov_chain(note_list, order=1, with_duration=False):
    '''
    Given a note list in the form of
    List[List[str, int/float], List[str, int/float], ...]
    [[<step>, <quaterlength>], [<step>, <quaterlength>], ...],
    returns a python defaultdict that represents the markov chain probabilities.
    Eace key of the returned dict is a tuple with length specified
    by "order", while each value is a python list with each element in the form
            1. (<step>, <quarterlength>) if "with_duration" is True or
            2. <step> otherwise.
    Notes that the length of note_list should be greater than "order", 
    otherwise an error may occur.
    '''
    if len(note_list) <= order:
        raise ValueError('Piece is too short.')

    trans_dic = defaultdict(list)
    if with_duration:
        prev_notes = [tuple(note) for note in note_list[-order:]]
    else:
        prev_notes = [note[0] for note in note_list[-order:]]

    for step, qlen in note_list:
        trans_dic[tuple(prev_notes)].append(
            (step, qlen) if with_duration else step)
        prev_notes.pop(0)
        prev_notes.append((step, qlen) if with_duration else step)

    return trans_dic


def compose_with_markov_chain(trans_dic, length=100, default_duration=0.5):
    '''
    Given the markov chain dictionary, returns a new piece of music
    with given length (equivilant to the numbers of notes and rests)
    by randomly "walking" through the markov chain.
    For example, if trans_dic = {('C4',): ('D4', 'D4', 'G4'), ...} and
    we choose 'C4' as the first note, then the probability of choosing
    'D4' as the second note would be 2/3.
    '''
    curr_steps = list(choice(list(trans_dic)))
    with_duration = isinstance(curr_steps[0], tuple)

    note_list = []

    for _ in range(length):
        n = choice(trans_dic[tuple(curr_steps)])
        note_list.append(n if with_duration else [n, 0.5])
        curr_steps.pop(0)
        curr_steps.append(n)

    return note_list


def parse_stream(stream_obj):
    '''
    Given a music21.stream.Stream object, returns a note list of form
    List[List[str, int/float], List[str, int/float], ...]
    [[<step>, <quaterlength>], [<step>, <quaterlength>], ...]
    Notes that if the stream consists of multiple parts, the highest
    part would be chosen. Likewise, if there's a chord in the stream,
    the highest note of the chord would be chosen.
    '''
    note_list = []
    if len(stream_obj.parts) > 0:
        stream_obj = stream_obj.parts[0]
    for n in stream_obj.recurse().notesAndRests.stream():
        if n.isRest:
            note_list.append(('R', n.quarterLength))
        elif n.isChord:
            n = n.sortAscending()[-1]
            note_list.append((n.nameWithOctave, n.quarterLength))
        else:
            note_list.append((n.nameWithOctave, n.quarterLength))
    return note_list


def generate_markov_matrix(trans_dic):
    '''
    Given the markov chain dictionary, print the probability matrix
    to stantard output. Returns nothing. The matrix would be in the
    following form:
    +---------+---------------------------------+
    |         | <note> <note> <note> ... <note> |
    +---------+---------------------------------+
    | <notes> |  1/3    2/3    0            0   |
    | <notes> |   0     2/7   4/7          1/7  |
    |   ...   |                     ...    ...  |
    | <notes> |  1/2     0     0    ...    1/2  |
    +---------+---------------------------------+
    Note: len(<notes>) equals to the order of markov chain
    '''
    keys = list(trans_dic)
    if len(keys[0]) == 1:       # if the order of markov chain is 1
        values = [n for n, in keys]
    else:
        values = set()
        for nlist in trans_dic.values():
            values |= set(nlist)
        values = list(values)

    value2index = {value: i for i, value in enumerate(values)}
    key2index = {value: i for i, value in enumerate(keys)}

    matrix = [[0] * len(values) for _ in range(len(keys))]
    for key, nlist in trans_dic.items():
        for n in nlist:
            matrix[key2index[key]][value2index[n]] += 1

    for i in range(len(matrix)):
        row_sum = sum(matrix[i])
        matrix[i] = [Fraction(x, row_sum) for x in matrix[i]]
        matrix[i].insert(
            0, str(keys[i])[1:-1].replace("'", "").replace(', ', ','))

    table = prettytable.PrettyTable()
    table.field_names = [
        ''] + [str(v).replace("'", "").replace(', ', ',') for v in values]
    for row in matrix:
        table.add_row(row)

    print(table)


def parse_args():
    '''
    Parses command line arguments out of sys.argv and returns
    an argparse.Namespace object. Notes that one and only one option
    among --json, --midi, --corpus should be present.
    '''
    parser = argparse.ArgumentParser()

    parser.add_argument('-l', '--length', type=int, default=100,
                        help='length of the new piece (number of notes)')
    parser.add_argument('--play', action='store_true',
                        help='play soundtrack')
    parser.add_argument('--score', action='store_true',
                        help='display score in a MusicXML reader')
    parser.add_argument('-o', '--order', type=int, default=1,
                        help='order of Markov chain (default: 1)')
    parser.add_argument('--original', action='store_true',
                        help='present the original piece of music')
    parser.add_argument('-d', '--with-duration', action='store_true',
                        help='treats notes with the same pitch and ' +
                        'different duration as different notes')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='increase verbosity level')

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-j', '--json', help='load form json format')
    group.add_argument('-m', '--midi', help='load from .midi file')
    group.add_argument('-c', '--corpus', help='load from music21 corpus')

    return parser.parse_args()


def main():
    args = parse_args()
    if args.verbose:
        print(args)

    if args.json:
        with open(args.json, 'r') as fin:
            try:
                in_piece = json.load(fin)
            except json.decoder.JSONDecodeError:
                print("[ERROR] Invalid File Format")
                raise
    elif args.corpus:
        in_piece = parse_stream(corpus.parse(args.corpus))
    elif args.midi:
        raise ValueError('Not implemented in this version.')

    if args.original:
        new_piece = in_piece
    else:
        trans_dic = calculate_markov_chain(
            in_piece, order=args.order, with_duration=args.with_duration)
        if args.verbose:
            print(trans_dic)
        generate_markov_matrix(trans_dic)
        new_piece = compose_with_markov_chain(trans_dic, length=args.length)
    if args.score or args.play:
        generate_stream(new_piece, play=args.play)


if __name__ == '__main__':
    main()
