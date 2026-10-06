// Example only: adapt to the app once we see its code.
//
// Plays the printing illustration while `printing` is true. When it turns
// false, the current receipt finishes, then the final receipt feeds out and
// holds in the Figma pose.
//
// New runtime (@rive-app/react-native), which drives the file's view model.
import { Text } from 'react-native';
import {
  RiveView,
  useRiveBoolean,
  useRiveFile,
  useViewModelInstance,
} from '@rive-app/react-native';
import { useEffect } from 'react';

type Props = { printing: boolean };

export function PosPrintingAnimation({ printing }: Props) {
  const { riveFile, error: fileError } = useRiveFile(require('./pos_printing.riv'));
  // The artboard's default view model (PosPrinting), "Default" instance.
  const { instance, error } = useViewModelInstance(riveFile, { async: true });
  const { setValue: setIsPrinting } = useRiveBoolean('isPrinting', instance);

  useEffect(() => {
    setIsPrinting(printing);
  }, [printing, setIsPrinting]);

  if (fileError || error) return <Text>{(fileError ?? error)!.message}</Text>;
  if (!riveFile || !instance) return null;

  // The artboard is 350 x 350, matching the Figma illustration's art area.
  return (
    <RiveView
      file={riveFile}
      dataBind={instance}
      autoPlay
      style={{ width: 350, height: 350 }}
    />
  );
}

// Legacy runtime (rive-react-native), for reference:
//
//   const [setRiveRef, riveRef] = useRive();
//   useEffect(() => { riveRef?.setBoolean('isPrinting', printing); }, [printing, riveRef]);
//   <Rive ref={setRiveRef} resourceName="pos_printing" stateMachineName="printing"
//         dataBinding={AutoBind(true)} style={{ width: 350, height: 350 }} />
