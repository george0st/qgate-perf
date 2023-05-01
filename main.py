import qgate_graph.graph as grp
import qgate_graph
import click
import logging

@click.command()
@click.option("--input", help="input directory (default is directory 'input'", default="input")
@click.option("--output", help="output directory (default is directory 'output'", default="output")
def graph(input,output):
    """Generate graphs based in input data."""
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)

    graph=grp.Graph()
    graph.generate_from_dir(input, output)

if __name__ == '__main__':
    graph()