import cv2
import numpy as np
import mediapipe as mp

class OctaviaFacialModeling:
    def __init__(self):
        """Initialize the Octavia facial modeling with blue lipstick emphasis"""
        # Initialize MediaPipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            min_detection_confidence=0.5
        )
        
        # Define lip indices in MediaPipe Face Mesh
        # These indices correspond to points around the lips
        self.lip_indices = [
            61, 146, 91, 181, 84, 17, 314, 405, 321, 375,
            291, 409, 270, 269, 267, 0, 37, 39, 40, 185
        ]
        
        # Define Octavia's signature blue color (RGB)
        self.octavia_blue = (0, 178, 255)  # RGB format
        self.octavia_blue_bgr = (255, 178, 0)  # BGR format for OpenCV
    
    def detect_face(self, image):
        """Detect face and extract landmarks using MediaPipe"""
        # Convert to RGB for MediaPipe
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(image_rgb)
        return results
    
    def create_lip_mask(self, image, results):
        """Create a mask for the lip region"""
        height, width = image.shape[:2]
        mask = np.zeros((height, width), dtype=np.uint8)
        
        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0]
            
            # Extract lip points
            lip_points = []
            for idx in self.lip_indices:
                landmark = face_landmarks.landmark[idx]
                x, y = int(landmark.x * width), int(landmark.y * height)
                lip_points.append([x, y])
            
            # Create polygon from lip points
            lip_points = np.array(lip_points, dtype=np.int32)
            cv2.fillPoly(mask, [lip_points], 255)
        
        return mask
    
    def apply_blue_lipstick(self, image, mask, intensity=0.8, metallic=True):
        """Apply Octavia's signature blue lipstick with optional metallic effect"""
        # Create blue lipstick layer
        lipstick_layer = np.zeros_like(image)
        lipstick_layer[mask > 0] = self.octavia_blue_bgr
        
        # Blend with original image
        result = cv2.addWeighted(image, 1.0, lipstick_layer, intensity, 0)
        
        if metallic:
            # Add metallic sheen effect
            sheen_mask = np.zeros_like(mask)
            height, width = mask.shape
            
            # Create gradient for sheen effect
            for i in range(height):
                for j in range(width):
                    if mask[i, j] > 0:
                        # Create a gradient based on position
                        gradient_value = int(255 * (j / width))
                        sheen_mask[i, j] = gradient_value
            
            # Apply sheen effect
            sheen_layer = np.zeros_like(image)
            sheen_layer[sheen_mask > 0] = (255, 255, 255)  # White sheen
            
            # Blend sheen with result
            result = cv2.addWeighted(result, 1.0, sheen_layer, 0.3, 0)
        
        return result
    
    def process_image(self, input_path, output_path):
        """Process an image to apply Octavia's blue lipstick"""
        # Read image
        image = cv2.imread(input_path)
        if image is None:
            print(f"Error: Could not read image {input_path}")
            return False
        
        # Detect face
        results = self.detect_face(image)
        
        if not results.multi_face_landmarks:
            print(f"No face detected in {input_path}")
            return False
        
        # Create lip mask
        lip_mask = self.create_lip_mask(image, results)
        
        # Apply blue lipstick
        result = self.apply_blue_lipstick(image, lip_mask)
        
        # Save result
        cv2.imwrite(output_path, result)
        print(f"Processed image saved to {output_path}")
        return True
    
    def process_video(self, input_path, output_path):
        """Process a video to apply Octavia's blue lipstick to each frame"""
        # Open video
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            print(f"Error: Could not open video {input_path}")
            return False
        
        # Get video properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        frame_number = 0
        
        # Initialize video face mesh
        video_face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Process frame
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = video_face_mesh.process(frame_rgb)
            
            if results.multi_face_landmarks:
                # Create lip mask
                lip_mask = self.create_lip_mask(frame, results)
                
                # Apply blue lipstick
                processed_frame = self.apply_blue_lipstick(frame, lip_mask)
                
                # Write processed frame
                out.write(processed_frame)
            else:
                # If no face detected, write original frame
                out.write(frame)
            
            frame_number += 1
            if frame_number % 10 == 0:
                print(f"Processed {frame_number}/{frame_count} frames")
        
        cap.release()
        out.release()
        print(f"Processed video saved to {output_path}")
        return True
    
    def visualize_landmarks(self, input_path, output_path):
        """Visualize facial landmarks with emphasis on lip region"""
        # Read image
        image = cv2.imread(input_path)
        if image is None:
            print(f"Error: Could not read image {input_path}")
            return False
        
        # Detect face
        results = self.detect_face(image)
        
        if not results.multi_face_landmarks:
            print(f"No face detected in {input_path}")
            return False
        
        # Draw landmarks
        face_landmarks = results.multi_face_landmarks[0]
        height, width = image.shape[:2]
        
        # Draw all landmarks
        for idx, landmark in enumerate(face_landmarks.landmark):
            x, y = int(landmark.x * width), int(landmark.y * height)
            cv2.circle(image, (x, y), 1, (0, 255, 0), -1)
        
        # Highlight lip landmarks
        for idx in self.lip_indices:
            landmark = face_landmarks.landmark[idx]
            x, y = int(landmark.x * width), int(landmark.y * height)
            cv2.circle(image, (x, y), 3, self.octavia_blue_bgr, -1)
        
        # Save result
        cv2.imwrite(output_path, image)
        print(f"Landmark visualization saved to {output_path}")
        return True


# Example usage
if __name__ == "__main__":
    octavia = OctaviaFacialModeling()
    
    # Process a single image
    octavia.process_image("input_image.jpg", "octavia_blue_lipstick.jpg")
    
    # Visualize landmarks
    octavia.visualize_landmarks("input_image.jpg", "octavia_landmarks.jpg")
    
    # Process a video (if available)
    # octavia.process_video("input_video.mp4", "octavia_blue_lipstick_video.mp4")
