import pandas as pd


def parse_dual_excel(coord_path,meta_path):
    coord_df=pd.read_excel(coord_path)
    coord_data=[]
    for _,row in coord_df.iterrows():
        coord_data.append({
            "pass":int(row[0]),
            "linetype":int(row[1]),
            "x1":float(row[2]) * 393.701,
            "y1":float(row[3]) * 393.701,
            "x2":float(row[4]) * 393.701,
            "y2":float(row[5]) * 393.701,
            "weight":float(row[6]),
            "delay":float(row[7]),
        })

    meta_df=pd.read_excel(meta_path,header=None)
    meta_dict={str(row[0]).strip().lower():list(row[1:]) for _,row in meta_df.iterrows()}

    origin={"x":None,"y":None}
    fiducials=[]
    height_sense_mode=None
    substrate_height=(0.0,0.0)

    # Valores por defecto para step repeat
    step_params={
        "start_point_x":0,
        "start_point_y":0,
        "pitch_x":1,
        "pitch_y":1,
        "pkg_width":1,
        "pkg_height":1
    }

    for key,vals in meta_dict.items():
        vals=list(vals)
        if "workpiece origin" in key:
            origin["x"],origin["y"]=float(vals[0]) * 393.701,float(vals[1]) * 393.701
        elif "fiducial 1" in key:
            fiducials.append((float(vals[0]) * 393.701,float(vals[1]) * 393.701,"F1"))
        elif "fiducial 2" in key:
            fiducials.append((float(vals[0]) * 393.701,float(vals[1]) * 393.701,"F2"))
        elif "height sense" in key:
            height_sense_mode=str(vals[0])
        elif "substrate height" in key:
            substrate_height=(float(vals[0]) * 393.701,float(vals[1]) * 393.701)
        elif "xy step distance" in key:
            step_params["pitch_x"],step_params["pitch_y"]=float(vals[0]) * 393.701,float(vals[1]) * 393.701
        elif "package origin offset" in key:
            step_params["start_point_x"],step_params["start_point_y"]=float(vals[0]) * 393.701,float(vals[1]) * 393.701
        elif "package width" in key:
            step_params["pkg_width"]=float(vals[0]) * 393.701
        elif "package height" in key:
            step_params["pkg_height"]=float(vals[1]) * 393.701

    return {
        "origin":origin,
        "fiducials":fiducials,
        "height_sense_mode":height_sense_mode,
        "substrate_height":substrate_height,
        "scale":393.701,
        "step_params":step_params,
        "excel_data":coord_data
    }
