// Write a soft foreground mask for the subject instance under a given point (Vision, macOS 14+).
import Vision; import AppKit; import CoreImage
let a = CommandLine.arguments
let url = URL(fileURLWithPath: a[1]); let out = URL(fileURLWithPath: a[2])
let px = Double(a[3])!, py = Double(a[4])!   // normalized point, origin top-left
let handler = VNImageRequestHandler(url: url)
let req = VNGenerateForegroundInstanceMaskRequest()
try handler.perform([req])
guard let r = req.results?.first else { print("no subject"); exit(1) }
// pick the instance under the point
let label = r.instanceMask
CVPixelBufferLockBaseAddress(label, .readOnly)
let w = CVPixelBufferGetWidth(label), h = CVPixelBufferGetHeight(label)
let base = CVPixelBufferGetBaseAddress(label)!.assumingMemoryBound(to: UInt8.self)
let row = CVPixelBufferGetBytesPerRow(label)
let id = base[Int(py*Double(h))*row + Int(px*Double(w))]
print("instances:", r.allInstances.count, "picked:", id)
let ids: IndexSet = id == 0 ? r.allInstances : IndexSet(integer: Int(id))
let mask = try r.generateScaledMaskForImage(forInstances: ids, from: handler)
let ci = CIImage(cvPixelBuffer: mask)
let rep = NSBitmapImageRep(ciImage: ci)
try rep.representation(using: .png, properties: [:])!.write(to: out)
