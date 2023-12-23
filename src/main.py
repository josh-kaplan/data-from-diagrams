from  mxgraph import MxGraph

def main():
    g = MxGraph('examples/activity.drawio.png')
    g.to_networkx(make_inferences=True)
    g.nx_plot()

if __name__ == "__main__":
    main()