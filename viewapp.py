import flask
import h5py
import os

source_dir = os.path.dirname(os.path.realpath(__file__))
app = flask.Flask(__name__, static_folder=os.path.join(source_dir, 'static'), static_url_path='')

data_dir = os.path.join(source_dir, '..', 'data')
hdf5_ext = '.h5'
valid_nonnumeric_chromosome_names = ['X', 'Y', 'M', 'MT']


def normalize_chr(chrom):
    """
    This function attempts to standardize how a chromosome is named.
    Eg.: both chrX and x will be mapped to X
    """
    chrom = str(chrom).upper()
    prefixes_to_remove = ['CHROMOSOME', 'CHR']
    for prefix in prefixes_to_remove:
        if chrom.startswith(prefix):
            chrom = chrom[len(prefix):]

    # make sure that the value is valid
    if not chrom in valid_nonnumeric_chromosome_names:
        # will throw a ValueError if this is not an int
        int(chrom)

    return chrom


def chr_cmp(chrom1, chrom2):
    """
    a comparison function for ordering chromosome names
    """

    chrom1 = normalize_chr(chrom1)
    chrom2 = normalize_chr(chrom2)

    def idx(xs, x):
        return xs.index(x) if x in xs else -1

    chrom1_idx = idx(valid_nonnumeric_chromosome_names, chrom1)
    chrom2_idx = idx(valid_nonnumeric_chromosome_names, chrom2)

    if chrom1_idx == -1 and chrom2_idx == -1:
        return cmp(int(chrom1), int(chrom2))
    elif chrom1_idx == -1:
        return -1
    elif chrom2_idx == -1:
        return 1
    else:
        return cmp(chrom1_idx, chrom2_idx)


@app.route('/experiment-<experiment_name>/sample-<sample_id>/chr<chr_id>/level-<int:level>/coords.json')
def get_coords(experiment_name, sample_id, chr_id, level):
    # TODO this is insecure!
    hdf5_file = h5py.File(os.path.join(data_dir, experiment_name + hdf5_ext), 'r')
   
    level_key = 'level{}'.format(level)
    chromosome_key = 'chr{}'.format(chr_id)

    level_group = hdf5_file[sample_id][chromosome_key][level_key]
    xyz_pos_list = [list(row) for row in level_group['coordinates']]
    genomic_coords_list = [
        [int(x) for x in row]
        for row in level_group['genomicPositions']
    ]

    return flask.jsonify(xyzPositions=xyz_pos_list, genomicCoords=genomic_coords_list)


@app.route('/experiment-<experiment_name>/sample-<sample_id>/chr<chr_id>/pet-interactions.json')
def get_protein_interactions(experiment_name, sample_id, chr_id):
    # TODO this is insecure!
    hdf5_file = h5py.File(os.path.join(data_dir, experiment_name + hdf5_ext), 'r')
    chromosome_key = 'chr{}'.format(chr_id)

    pet_group = hdf5_file[sample_id][chromosome_key]['Pet_Group']
    pet_interaction = [
        [int(x) for x in row]
        for row in pet_group['petInteractions']
    ]

    return flask.jsonify(petInteractions=pet_interaction)


@app.route('/all-models-metadata.json')
def get_all_models_metadata():
    experiment_names = []
    experiments = dict()
    for file in os.listdir(data_dir):
        if file.endswith(hdf5_ext):
            print 'file: ', os.path.join(data_dir, file)

            curr_exp_hdf5 = h5py.File(os.path.join(data_dir, file), 'r')

            sample_names = [k for k in curr_exp_hdf5.iterkeys() if not k.startswith('__')]
            samples = dict()
            for sample_name in sample_names:
                print 'sample_name: ', sample_name

                curr_sample_hdf5 = curr_exp_hdf5[sample_name]
                chr_names = curr_sample_hdf5.keys()
                chr_names.sort(cmp=chr_cmp)

                protein_factors = []
                level_count = 0
                for chr in chr_names:
                    curr_chr_hdf5 = curr_sample_hdf5[chr]
                    protein_factors = list(curr_chr_hdf5['Pet_Group']['proteinFactors'])
                    for k in curr_chr_hdf5.iterkeys():
                        if k.startswith('level'):
                            level_count += 1
                    break

                samples[sample_name] = {
                    'chromosomeNames': chr_names,
                    'proteinFactors': protein_factors,
                    'levelCount': level_count,
                }

            experiment_name = file[: -len(hdf5_ext)]
            experiment_names.append(experiment_name)
            curr_experiment = {
                'experimentName': experiment_name,
                'sampleNames': sample_names,
                'samples': samples,
            }
            experiments[experiment_name] = curr_experiment

    return flask.jsonify(
        experimentNames=experiment_names,
        experiments=experiments)


@app.route('/levels.json')
def get_levels():
    return flask.jsonify(levels=list(xrange(4)))


if __name__ == '__main__':
    app.debug = True
    app.run()
