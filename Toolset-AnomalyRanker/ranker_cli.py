import csv
import os
import multiprocessing

import click
import pendulum

import ranker_app


@click.command()
@click.option('--label', type=str, required=False)
@click.option('--timeout', type=int, default=None)
@click.option('--output', type=click.Path())
@click.argument('gml_file', type=click.Path(exists=True), required=True)
def cli(label, timeout, output, gml_file):
    if not label:
        label = os.path.basename(gml_file)

    api_client = ranker_app.app.test_client()
    with open(gml_file, mode='r') as gml_file:
        gml_string = gml_file.read()
    api_data = {
        'gml': gml_string,
    }

    def target(result):
        api_response = api_client.post('/rank', json=api_data)
        if api_response.status_code == 200:
            result['success'] = True
            result['data'] = api_response.data.decode("utf-8").rstrip().replace('"', '\\"')
        else:
            result['success'] = False
            result['data'] = ''

    process_manager = multiprocessing.Manager()
    process_result = process_manager.dict()
    process = multiprocessing.Process(target=target, args=(process_result,))
    process.daemon = True

    start_time = pendulum.now()
    process.start()

    process.join(timeout)
    if process.is_alive():
        process.terminate()
        process_result['success'] = False
        process_result['data'] = ''

    execution_time = pendulum.now() - start_time
    output_row = [label, process_result['success'], execution_time.in_seconds(), process_result['data']]

    if output:
        with open(output, mode='a') as output:
            csv_writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC, lineterminator='\n')
            csv_writer.writerow(output_row)
    print(output_row)


if __name__ == '__main__':
    cli()
