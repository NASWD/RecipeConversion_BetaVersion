
from collections import defaultdict
import os
from datetime import datetime
from PyQt5.QtWidgets import QMessageBox


def parse_wafer_map_file(filepath):
    try:
        with open(filepath,"r") as file:
            content=file.read().strip()
        dies={}
        for entry in content.split(";"):
            parts=entry.strip().split(",")
            if len(parts)==4:
                die_id=int(parts[0])
                x=int(parts[1])
                y=int(parts[2])
                die_type=parts[3].strip().upper()
                dies[(x,y)]=die_type
        return dies
    except Exception as e:
        print("Failed to parse wafer map:",e)
        return {}


def build_clean_fmw(file_paths,coord_data,origin,fiducials,scale,substrate_height,
                    filenames=None,wafer_map_path=None,user_step_repeat=None,output_path=None):
    date_str=datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_folder="output"
    os.makedirs(output_folder,exist_ok=True)
    output_path=os.path.join(output_folder,f"program_{date_str}.fmw")

    use_wafer_map=False
    wafer_map={}

    if wafer_map_path and os.path.exists(wafer_map_path):
        reply=QMessageBox.question(
            None,
            "Integrate Wafer Map?",
            "Wafer map detected. Use it to repeat the pattern across dies (step and repeat)?",
            QMessageBox.Yes|QMessageBox.No
        )
        use_wafer_map=(reply==QMessageBox.Yes)
        if use_wafer_map:
            wafer_map=parse_wafer_map_file(wafer_map_path)

    try:
        with open(output_path,"w") as f:
            # HEADER
            f.write(".header\n")
            f.write("version = 5.5\n")
            f.write("units = mm\n")
            f.write("macro = Workpiece\n")
            f.write("cursorLoc = 7\n")
            f.write(f"fluid1Filename = {filenames.get('fluid1','')}\n")
            f.write(f"fluid2Filename = {filenames.get('fluid2','')}\n")
            f.write(f"heater1Filename = {filenames.get('heater1','')}\n")
            f.write(f"heater2Filename = {filenames.get('heater2','')}\n")
            f.write(f"heater3Filename = {filenames.get('heater3','')}\n")
            f.write(f"heater4Filename = {filenames.get('heater4','')}\n")
            f.write("Attach Fluid File = ON\n")
            f.write("Attach Heater File = ON\n")
            f.write("Valve 1 Refill Mode = At Start Of Prod, Every 1 Run(s)\n")
            f.write("Valve 2 Refill Mode = At Start Of Prod, Every 1 Run(s)\n")
            f.write("Move to First Fid Location = OFF\n")
            f.write("Move To System Location = OFF\n")
            f.write("System Location Name = VALVE 1 PURGE LOC\n")
            f.write("Set Active Valve = 0\n")
            f.write("Batch Fids = ON\n")
            f.write("Pipeline Vision = ON\n")
            f.write("Find Fids On-the-Fly = OFF\n")
            f.write("Use FoF High-Accuracy Mode = OFF\n")
            f.write("FoF High-Accuracy Trigger Angle (deg) = 90.000000\n")
            f.write("Automatic Conveyor Width = 0.000000\n")
            f.write("Automatic Conveyor Width Tolerance = 250.000000\n")
            f.write("Automatic Conveyor Width Enabled = OFF\n")
            f.write("Automatic Conveyor 2 Width = 0.000000\n")
            f.write("Automatic Conveyor 2 Width Tolerance = 250.000000\n")
            f.write("Automatic Conveyor 2 Width Enabled = OFF\n")
            f.write("CAD Import Generated File = OFF\n")
            f.write("Force HS on new pattern (HS SEL Only) = OFF\n")
            f.write("Fid Search At Safe Z = ON\n")
            f.write("Batch Height Sense Commands = ON\n")
            f.write("Batch Height Sense Probe Down = OFF\n")
            f.write("Pre-Heat Time = 0\n")
            f.write("Apply Camera Rotation Correction = OFF\n")
            f.write("Max time board remains at dispense(sec) = 0\n")
            f.write("Dual Dispense MFC Tolerance = 0.000000\n")
            f.write("Default Runtime Light Level Enabled = OFF\n")
            f.write("Default Runtime Light Level 1 = 0\n")
            f.write("Default Runtime Light Level 2 = 0\n")
            f.write("Default Runtime Light Level 3 = 0\n")
            f.write("Map File Control (ON/OFF) = OFF\n")
            f.write("Conveyor 1 Mode = -1\n")
            f.write("Conveyor 2 Mode = -1\n")
            f.write("Dual Valve Key Pattern = \n")
            f.write("Pocket Depth of Carrier = 0.000000\n")
            f.write("Substrate Thickness = 0.000000\n")
            f.write("Barcode Disable = OFF\n")
            f.write("Workpiece Fiducial Failure Mode = 0\n")
            f.write("Map Origin Used In Program = 3\n")
            f.write("ESR99_015478 Parms = \n")
            f.write("Board Unit Count = 1\n")
            f.write("Use Program Max Height Sense Search Depth = OFF\n")
            f.write("Program Max Height Sense Search Depth (FMW) = 0.000000\n")
            f.write("ADS Program Pitch(mm) = -1.000000\n")
            f.write("Unit Counting Pattern = \n")
            f.write("Recipe LMO Mode = 0\n")
            f.write("ESR7283540 Heater Monitor Parm List = \n")
            # SETTINGS
            f.write(".end\n")

            # MAIN
            f.write(".main\n")
            f.write("SET HEIGHT SENSE MODE: 1, OnCommand, 0.000, (0.000000, 0.000000), 0.000, (0.000000, 0.000000)\n")
            f.write("SET ZFAST MODE: OFF\n")
            f.write(f"DO: Workpiece AT ({origin['x']:.6f}, {origin['y']:.6f}), 0.000000, 0.000000\n")
            f.write(".end\n")

            # PROCLIST
            f.write(".proclist\n")
            f.write(".endproclist\n")

            # PATTLIST
            f.write(".pattlist\n")

            f.write(".patt: Workpiece\n")

            f.write(f".ref frame: {origin['x']:.6f}, {origin['y']:.6f}, 0.000000\n")

            # FIDUCIALS BLOCK FOR Workpiece
            f.write(".findinfo\n")
            f.write("[Two-Fid Frame Find]\n\n")
            for i,(x,y,name) in enumerate(fiducials,1):
                f.write(f".fid{i}\n")
                f.write("[Model Finder]\n")
                f.write(f"Fid Name = Fid {i}\n")
                f.write(f"Expected Loc = {x:.3f},{y:.3f},0.000\n")
                f.write("Expected Angle (loc degs) = 0.000000\n")
                f.write("Owner Name = Workpiece\n")
                f.write("Is Valid = ON\n")
                f.write("Check Tol = ON\n")
                f.write("Use Local Tol = OFF\n")
                f.write("Local Tol = 0.000000\n")
                f.write("Light Level = 0\n")
                for j in range(1,6):
                    if j <= 3:
                        level = "59.706960"
                    else:
                        level = "0.000000"
                    f.write(f"Light {j} Level = {level}\n")
                    f.write(f"Shutter {j} Open = ON\n")
                    f.write(f"Light {j} Pixel Avg = -1.000000\n")
                f.write("Settling Time (msecs) = 50\n")
                f.write("Camera Gain (0->12) = 0.000000\n")
                f.write("Camera LUT Gamma (0.5->1.5) = 1.000000\n")
                f.write("Fiducial Fail Option = 0\n")
                f.write("Pause After Search = 1\n")
                f.write("Min Fid Acceptance Confidence Level = 80.000000\n")
                f.write("Max Fid Acceptance Confidence Level = 0.000000\n")
                f.write("Min Fid Prompt Confidence Level = 50.000000\n")
                f.write("Use Local Fid-Not-Found Option = 0 \n")
                f.write("Num Models = 1\n\n")

                f.write(f".endfid{i}\n")

            # HEIGHT
            if substrate_height:
                x_sh,y_sh=substrate_height

                f.write(".endfindinfo\n")
                f.write(".skipinfo\n\n")

                f.write(".endskipinfo\n")
                f.write(".substrateidinfo\n")
                f.write(".endsubstrateidinfo\n")
                f.write(".locinfo\n\n")

                f.write(".endlocinfo\n")
                f.write(".moduleinfo\n")
                f.write("Defines Module IDs = OFF\n")
                f.write(".endmoduleinfo\n")
                f.write(".fidcontrolinfo\n")
                f.write("false\n")
                f.write(".endfidcontrolinfo\n")
                f.write("LOG COMMENT: Find Height Once Per Wafer\n")
                f.write(f"FIND SUBSTRATE HEIGHT: ({x_sh:.6f}, {y_sh:.6f})\n")
                passes=sorted(set(row["pass"] for row in coord_data))
                first_pass = min(passes)
                last_pass = max(passes)
                f.write(f"LOOP PASS: FROM {first_pass} TO {last_pass} \n")  # HARDCODED BUT COMEBACK TO ADD REAL VALUES

            # Defaults
            pitch_x=user_step_repeat.get("pitch_x",1)
            pitch_y=user_step_repeat.get("pitch_y",1)
            # Compute rows and columns from wafer_map
            all_coords=list(wafer_map.keys())
            if all_coords:
                x_indices = {x for x, _ in all_coords}
                y_indices = {y for _, y in all_coords}
                columns = len(x_indices)
                rows = len(y_indices)
            else:
                columns=1
                rows=1
            f.write(
                f"STEP AND REPEAT: Wafer Map, "
                f"(0.000000,0.000000), "
                f"({pitch_x:.6f},0.000000), "
                f"(0.000000,{pitch_y:.6f}), "
                f"1,{rows},{columns},1,0,1, "
                f"[MAP: 0;(0,0);0;0], "
                f"0,(0.000000,0.000000), "
                f"(0.000000,0.000000), "
                f"(0.000000,0.000000), "
                f"WRC:1,1,0.000000,0.000000,TBV=0\n"
            )

            f.write("LOG COMMENT: Go to next loop\n")
            f.write("NEXT LOOP: \n")
            # After all passes, final WAIT for last pass delay if any
            # PASS SECTIONS
            num_passes=len(passes)
            last_pass=passes[-1]
            last_delay=next(
                (r["delay"] for r in coord_data if r["pass"]==last_pass and r["delay"]>0),
                0
            )
            if last_delay>0:
                f.write(f"WAIT: {int(last_delay)}.000, Pass {last_pass} timer\n")
            f.write(".end\n")

            # PATTLIST
            f.write(".patt: Line\n")
            f.write(".ref frame: 0.000000, 0.000000, 0.000000\n")
            f.write(".findinfo\n\n")

            f.write(".endfindinfo\n")
            f.write(".skipinfo\n\n")

            f.write(".endskipinfo\n")
            f.write(".substrateidinfo\n")
            f.write(".endsubstrateidinfo\n")
            f.write(".locinfo\n\n")

            f.write(".endlocinfo\n")
            f.write(".moduleinfo\n")
            f.write("Defines Module IDs = OFF\n")
            f.write(".endmoduleinfo\n")
            f.write(".fidcontrolinfo\n")
            f.write("false\n")
            f.write(".endfidcontrolinfo\n")

            for i,pass_num in enumerate(passes):
                f.write(f"START PASS: FOR PASS {pass_num}\n")
                # Si no es el primer pass, imprime AWAIT MULTIPASS TIMER al inicio
                if i>0:
                    prev_pass=passes[i-1]
                    prev_delay=next(
                        (r["delay"] for r in coord_data if r["pass"]==prev_pass and r["delay"]>0),
                        0
                    )
                    if prev_delay>0:
                        f.write(
                            f"AWAIT MULTIPASS TIMER: {int(prev_delay)}, Pass {prev_pass} timer~{int(prev_delay)},0\n"
                        )
                # WEIGHT CONTROL
                for row in coord_data:
                    if row["pass"]!=pass_num:
                        continue
                    f.write(
                        f"WEIGHT CONTROL: 2,{row['weight']:.3f},{row['linetype']},1,1,1.0000,0,"
                        f"({row['x1']:.3f},{row['y1']:.3f}),({row['x2']:.3f},{row['y2']:.3f}),1,\n"
                    )
                # Si no es el último pass, imprime RESET MULTIPASS TIMER al final
                if i<num_passes-1:
                    f.write("RESET MULTIPASS TIMER: \n")
                f.write("END PASS:\n")

            f.write("COMMENT: End of Customer Coords.\n")
            f.write(".end\n")

            # SECOND .PATT: Wafer Map
            if use_wafer_map and user_step_repeat:
                f.write(".patt: Wafer Map\n")
                f.write(".ref frame: 0.000000, 0.000000, 0.000000\n")
                f.write(".findinfo\n\n")

                f.write(".endfindinfo\n")
                f.write(".skipinfo\n\n")

                f.write(".endskipinfo\n")
                f.write(".substrateidinfo\n")
                f.write(".endsubstrateidinfo\n")
                f.write(".locinfo\n\n")

                f.write(".endlocinfo\n")

                f.write(".moduleinfo\n")
                f.write("Defines Module IDs = OFF\n")
                f.write(".endmoduleinfo\n")
                f.write(".fidcontrolinfo\n")
                f.write("false\n")
                f.write(".endfidcontrolinfo\n")

                start_x=user_step_repeat.get("start_point_x",0)
                start_y=user_step_repeat.get("start_point_y",0)
                pitch_x=user_step_repeat.get("pitch_x",1)
                pitch_y=user_step_repeat.get("pitch_y",1)

                for idx,(die_x,die_y) in enumerate(wafer_map.keys(),1):
                    step_x=die_x * pitch_x+start_x
                    step_y=die_y * pitch_y+start_y
                    f.write(f"COMMENT: Part {idx}\n")
                    f.write(f"DO MULTIPASS: Line AT ({step_x:.6f}, {step_y:.6f}), 0.000000, 0.000000\n")

            f.write(".end\n")
            f.write(".endpattlist\n")
            f.write(".prefid\n")
            f.write(".end\n")
            # Show popup with file created and option to open

            msg_box=QMessageBox()

            msg_box.setIcon(QMessageBox.Information)

            msg_box.setWindowTitle("FMW File Created")

            msg_box.setText(f"✅ File successfully created:\n{output_path}")

            msg_box.setStandardButtons(QMessageBox.Open|QMessageBox.Close)

            ret=msg_box.exec_()

            if ret==QMessageBox.Open:
                # os.system(f'xdg-open "{output_path}"')  # Linux

                os.startfile(output_path)  # Windows alternative (uncomment if on Windows)

        return output_path,len(coord_data)
    except Exception as e:
        raise RuntimeError(f"❌ Failed to generate FMW file: {e}")
