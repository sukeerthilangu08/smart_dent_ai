import cv2
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import json
from PIL import Image
import io
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DentalAIModel:
    def __init__(self):
        self.model_loaded = True
        self.analysis_history = []
        
    def is_loaded(self) -> bool:
        """Check if the model is loaded and ready"""
        return self.model_loaded
    
    def preprocess_image(self, image: Image.Image) -> np.ndarray:
        """Enhanced image preprocessing for dental analysis"""
        try:
            # Convert PIL Image to numpy array
            if isinstance(image, Image.Image):
                image_array = np.array(image)
            else:
                image_array = image
            
            # Ensure RGB format
            if len(image_array.shape) == 3 and image_array.shape[2] == 3:
                # Already RGB
                rgb_image = image_array
            else:
                # Convert if needed
                rgb_image = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
            
            # Resize to standard size for analysis
            resized = cv2.resize(rgb_image, (512, 512))
            
            # Normalize to 0-1 range
            normalized = resized.astype(np.float32) / 255.0
            
            return normalized
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {str(e)}")
            raise
    
    def detect_teeth_region(self, image: np.ndarray) -> np.ndarray:
        """Detect teeth regions in the image using advanced techniques"""
        try:
            # Convert to different color spaces for better tooth detection
            gray = cv2.cvtColor((image * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
            lab = cv2.cvtColor((image * 255).astype(np.uint8), cv2.COLOR_RGB2LAB)
            hsv = cv2.cvtColor((image * 255).astype(np.uint8), cv2.COLOR_RGB2HSV)
            
            # Method 1: Brightness-based detection (teeth are usually brighter)
            bright_threshold = np.percentile(gray, 75)
            bright_mask = gray > bright_threshold
            
            # Method 2: Color-based detection in LAB space
            l_channel = lab[:, :, 0]
            a_channel = lab[:, :, 1]
            b_channel = lab[:, :, 2]
            
            # Teeth typically have high L (lightness) and low a,b variations
            teeth_mask_lab = (l_channel > 120) & (np.abs(a_channel - 128) < 20)
            
            # Method 3: HSV-based detection
            # Teeth colors typically have low saturation and high value
            h_channel = hsv[:, :, 0]
            s_channel = hsv[:, :, 1]
            v_channel = hsv[:, :, 2]
            
            teeth_mask_hsv = (s_channel < 80) & (v_channel > 150)
            
            # Combine all methods
            combined_mask = bright_mask & teeth_mask_lab & teeth_mask_hsv
            
            # Clean up the mask with morphological operations
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            cleaned_mask = cv2.morphologyEx(combined_mask.astype(np.uint8), cv2.MORPH_OPEN, kernel)
            cleaned_mask = cv2.morphologyEx(cleaned_mask, cv2.MORPH_CLOSE, kernel)
            
            # Remove small noise
            cleaned_mask = cv2.medianBlur(cleaned_mask, 5)
            
            return cleaned_mask.astype(bool)
            
        except Exception as e:
            logger.error(f"Error detecting teeth region: {str(e)}")
            # Return a fallback mask
            return np.ones((image.shape[0], image.shape[1]), dtype=bool)
    
    def analyze_tooth_yellowness(self, image: np.ndarray, teeth_mask: np.ndarray) -> Dict:
        """Advanced yellowness detection using multiple color spaces"""
        try:
            # Convert to different color spaces
            lab = cv2.cvtColor((image * 255).astype(np.uint8), cv2.COLOR_RGB2LAB)
            hsv = cv2.cvtColor((image * 255).astype(np.uint8), cv2.COLOR_RGB2HSV)
            
            # Extract teeth pixels only
            if np.sum(teeth_mask) == 0:
                return {
                    "condition": "tooth_yellowness",
                    "yellowness_score": 0.0,
                    "severity": "Cannot detect teeth",
                    "whiteness_level": 0.0,
                    "recommendations": ["Please retake photo with better lighting and teeth visibility"]
                }
            
            # LAB color space analysis (most accurate for yellowness)
            l_channel = lab[:, :, 0][teeth_mask]
            a_channel = lab[:, :, 1][teeth_mask]
            b_channel = lab[:, :, 2][teeth_mask]
            
            # Calculate yellowness metrics
            mean_lightness = np.mean(l_channel)
            mean_a = np.mean(a_channel)
            mean_b = np.mean(b_channel)
            
            # In LAB space, positive b values indicate yellow
            # Normal teeth should have b values around 128 (neutral)
            yellowness_b = (mean_b - 128) / 127.0  # Normalize to -1 to 1
            yellowness_b = max(0, yellowness_b)  # Only positive values (yellow)
            
            # HSV analysis for additional yellowness detection
            h_channel = hsv[:, :, 0][teeth_mask]
            s_channel = hsv[:, :, 1][teeth_mask]
            v_channel = hsv[:, :, 2][teeth_mask]
            
            # Yellow hue range in HSV (approximately 20-30 degrees)
            yellow_hue_mask = (h_channel >= 15) & (h_channel <= 35)
            yellow_hue_percentage = np.sum(yellow_hue_mask) / len(h_channel)
            
            # Combine yellowness metrics
            yellowness_score = (yellowness_b * 0.7 + yellow_hue_percentage * 0.3)
            yellowness_score = min(1.0, max(0.0, yellowness_score))
            
            # Calculate whiteness level (higher is whiter)
            whiteness_level = mean_lightness / 255.0
            
            # Adjust yellowness based on overall brightness
            if whiteness_level < 0.4:
                yellowness_score *= 1.2  # Increase penalty for dark yellow teeth
            
            # Determine severity
            if yellowness_score < 0.15:
                severity = "Excellent - Very white teeth"
            elif yellowness_score < 0.3:
                severity = "Good - Slight yellowness"
            elif yellowness_score < 0.5:
                severity = "Fair - Moderate yellowness"
            elif yellowness_score < 0.7:
                severity = "Poor - Significant yellowness"
            else:
                severity = "Critical - Severe yellowness"
            
            # Generate recommendations
            recommendations = []
            if yellowness_score > 0.2:
                recommendations.extend([
                    "Brush teeth twice daily with whitening toothpaste",
                    "Reduce consumption of coffee, tea, and red wine",
                    "Avoid smoking and tobacco products"
                ])
            if yellowness_score > 0.4:
                recommendations.extend([
                    "Consider professional teeth whitening treatment",
                    "Use whitening mouthwash daily",
                    "Schedule dental cleaning every 6 months"
                ])
            if yellowness_score > 0.6:
                recommendations.extend([
                    "Consult dentist for advanced whitening options",
                    "Consider in-office whitening procedures",
                    "Evaluate underlying causes of discoloration"
                ])
            
            if yellowness_score <= 0.15:
                recommendations.extend([
                    "Maintain excellent oral hygiene",
                    "Continue current dental care routine",
                    "Regular dental checkups to maintain whiteness"
                ])
            
            return {
                "condition": "tooth_yellowness",
                "yellowness_score": round(yellowness_score, 3),
                "severity": severity,
                "whiteness_level": round(whiteness_level, 3),
                "lab_b_value": round(mean_b, 2),
                "yellow_hue_percentage": round(yellow_hue_percentage * 100, 2),
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"Error analyzing yellowness: {str(e)}")
            return {
                "condition": "tooth_yellowness",
                "yellowness_score": 0.0,
                "severity": "Error in analysis",
                "whiteness_level": 0.0,
                "recommendations": ["Please retake photo for analysis"]
            }
    
    def detect_basic_dental_flaws(self, image: np.ndarray, teeth_mask: np.ndarray) -> Dict:
        """Detect basic dental flaws like dark spots, irregularities, and visible issues"""
        try:
            gray = cv2.cvtColor((image * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
            
            if np.sum(teeth_mask) == 0:
                return {
                    "condition": "dental_flaws",
                    "flaw_score": 0.0,
                    "issues_detected": [],
                    "severity": "Cannot analyze",
                    "recommendations": ["Please retake photo with clearer teeth visibility"]
                }
            
            # Apply mask to focus on teeth only
            teeth_gray = gray.copy()
            teeth_gray[~teeth_mask] = 255  # Set non-teeth areas to white
            
            issues_detected = []
            flaw_scores = []
            
            # 1. Dark Spot Detection (potential cavities/stains)
            dark_spots = self._detect_dark_spots(teeth_gray, teeth_mask)
            if dark_spots["severity"] != "None":
                issues_detected.append(f"Dark spots detected: {dark_spots['severity']}")
                flaw_scores.append(dark_spots["score"])
            
            # 2. Edge Irregularities (chips, cracks)
            edge_issues = self._detect_edge_irregularities(teeth_gray, teeth_mask)
            if edge_issues["severity"] != "None":
                issues_detected.append(f"Edge irregularities: {edge_issues['severity']}")
                flaw_scores.append(edge_issues["score"])
            
            # 3. Surface Texture Analysis
            texture_issues = self._analyze_surface_texture(teeth_gray, teeth_mask)
            if texture_issues["severity"] != "None":
                issues_detected.append(f"Surface irregularities: {texture_issues['severity']}")
                flaw_scores.append(texture_issues["score"])
            
            # 4. Plaque/Tartar Detection
            plaque_issues = self._detect_plaque_tartar(image, teeth_mask)
            if plaque_issues["severity"] != "None":
                issues_detected.append(f"Plaque/tartar buildup: {plaque_issues['severity']}")
                flaw_scores.append(plaque_issues["score"])
            
            # Calculate overall flaw score
            if flaw_scores:
                overall_flaw_score = np.mean(flaw_scores)
            else:
                overall_flaw_score = 0.0
            
            # Determine overall severity
            if overall_flaw_score < 0.2:
                severity = "Excellent - No significant flaws"
            elif overall_flaw_score < 0.4:
                severity = "Good - Minor issues"
            elif overall_flaw_score < 0.6:
                severity = "Fair - Moderate issues"
            elif overall_flaw_score < 0.8:
                severity = "Poor - Multiple issues"
            else:
                severity = "Critical - Severe issues"
            
            # Generate recommendations
            recommendations = []
            if overall_flaw_score > 0.3:
                recommendations.extend([
                    "Schedule a dental examination",
                    "Improve daily oral hygiene routine",
                    "Consider professional cleaning"
                ])
            if overall_flaw_score > 0.5:
                recommendations.extend([
                    "Urgent dental consultation recommended",
                    "Address visible dental issues promptly",
                    "Professional treatment may be required"
                ])
            if overall_flaw_score <= 0.2:
                recommendations.extend([
                    "Maintain excellent oral care",
                    "Continue regular dental checkups",
                    "Keep up good oral hygiene habits"
                ])
            
            return {
                "condition": "dental_flaws",
                "flaw_score": round(overall_flaw_score, 3),
                "issues_detected": issues_detected,
                "severity": severity,
                "detailed_analysis": {
                    "dark_spots": dark_spots,
                    "edge_irregularities": edge_issues,
                    "surface_texture": texture_issues,
                    "plaque_tartar": plaque_issues
                },
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"Error detecting dental flaws: {str(e)}")
            return {
                "condition": "dental_flaws",
                "flaw_score": 0.0,
                "issues_detected": [],
                "severity": "Error in analysis",
                "recommendations": ["Please retake photo for analysis"]
            }
    
    def _detect_dark_spots(self, gray_image: np.ndarray, teeth_mask: np.ndarray) -> Dict:
        """Detect dark spots that might indicate cavities or stains"""
        try:
            # Calculate threshold for dark spots
            teeth_pixels = gray_image[teeth_mask]
            if len(teeth_pixels) == 0:
                return {"severity": "None", "score": 0.0}
            
            mean_brightness = np.mean(teeth_pixels)
            std_brightness = np.std(teeth_pixels)
            
            # Dark spots threshold
            dark_threshold = mean_brightness - 1.5 * std_brightness
            dark_spots = (gray_image < dark_threshold) & teeth_mask
            
            # Remove noise with morphological operations
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            dark_spots = cv2.morphologyEx(dark_spots.astype(np.uint8), cv2.MORPH_OPEN, kernel)
            
            # Find contours of dark spots
            contours, _ = cv2.findContours(dark_spots, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Analyze dark spots
            significant_spots = 0
            total_dark_area = 0
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 15:  # Minimum area for significant spot
                    significant_spots += 1
                    total_dark_area += area
            
            # Calculate score
            teeth_area = np.sum(teeth_mask)
            dark_area_ratio = total_dark_area / teeth_area if teeth_area > 0 else 0
            
            score = min(1.0, dark_area_ratio * 20 + significant_spots * 0.1)
            
            if score < 0.2:
                severity = "None"
            elif score < 0.4:
                severity = "Mild"
            elif score < 0.6:
                severity = "Moderate"
            else:
                severity = "Severe"
            
            return {
                "severity": severity,
                "score": score,
                "spots_count": significant_spots,
                "dark_area_percentage": round(dark_area_ratio * 100, 2)
            }
            
        except Exception as e:
            logger.error(f"Error detecting dark spots: {str(e)}")
            return {"severity": "None", "score": 0.0}
    
    def _detect_edge_irregularities(self, gray_image: np.ndarray, teeth_mask: np.ndarray) -> Dict:
        """Detect edge irregularities that might indicate chips or cracks"""
        try:
            # Find edges using Canny edge detection
            edges = cv2.Canny(gray_image, 50, 150)
            
            # Focus on teeth edges only
            teeth_edges = edges & teeth_mask
            
            # Find contours of teeth
            contours, _ = cv2.findContours(teeth_mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            irregularity_score = 0.0
            total_perimeter = 0
            
            for contour in contours:
                if cv2.contourArea(contour) > 100:  # Minimum area for tooth
                    # Calculate contour smoothness
                    epsilon = 0.02 * cv2.arcLength(contour, True)
                    smooth_contour = cv2.approxPolyDP(contour, epsilon, True)
                    
                    # More points in approximation = more irregular
                    irregularity = len(smooth_contour) / cv2.arcLength(contour, True)
                    irregularity_score += irregularity
                    total_perimeter += cv2.arcLength(contour, True)
            
            if total_perimeter > 0:
                normalized_score = min(1.0, irregularity_score / 10)
            else:
                normalized_score = 0.0
            
            if normalized_score < 0.2:
                severity = "None"
            elif normalized_score < 0.4:
                severity = "Mild"
            elif normalized_score < 0.6:
                severity = "Moderate"
            else:
                severity = "Severe"
            
            return {
                "severity": severity,
                "score": normalized_score,
                "edge_complexity": round(irregularity_score, 3)
            }
            
        except Exception as e:
            logger.error(f"Error detecting edge irregularities: {str(e)}")
            return {"severity": "None", "score": 0.0}
    
    def _analyze_surface_texture(self, gray_image: np.ndarray, teeth_mask: np.ndarray) -> Dict:
        """Analyze surface texture for irregularities"""
        try:
            # Apply Gaussian blur to get base surface
            blurred = cv2.GaussianBlur(gray_image, (5, 5), 0)
            
            # Calculate texture by finding difference from smooth surface
            texture = np.abs(gray_image.astype(np.float32) - blurred.astype(np.float32))
            
            # Focus on teeth area
            teeth_texture = texture[teeth_mask]
            
            if len(teeth_texture) == 0:
                return {"severity": "None", "score": 0.0}
            
            # Calculate texture metrics
            mean_texture = np.mean(teeth_texture)
            std_texture = np.std(teeth_texture)
            
            # Normalize texture score
            texture_score = min(1.0, (mean_texture + std_texture) / 50)
            
            if texture_score < 0.2:
                severity = "None"
            elif texture_score < 0.4:
                severity = "Mild"
            elif texture_score < 0.6:
                severity = "Moderate"
            else:
                severity = "Severe"
            
            return {
                "severity": severity,
                "score": texture_score,
                "texture_variance": round(std_texture, 2)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing surface texture: {str(e)}")
            return {"severity": "None", "score": 0.0}
    
    def _detect_plaque_tartar(self, image: np.ndarray, teeth_mask: np.ndarray) -> Dict:
        """Detect plaque and tartar buildup"""
        try:
            # Convert to HSV for better color detection
            hsv = cv2.cvtColor((image * 255).astype(np.uint8), cv2.COLOR_RGB2HSV)
            
            # Define color ranges for plaque/tartar (yellowish-brown)
            lower_plaque = np.array([10, 50, 50])
            upper_plaque = np.array([30, 255, 200])
            
            # Create mask for plaque colors
            plaque_mask = cv2.inRange(hsv, lower_plaque, upper_plaque)
            
            # Combine with teeth mask
            plaque_on_teeth = plaque_mask & teeth_mask.astype(np.uint8) * 255
            
            # Calculate plaque coverage
            teeth_area = np.sum(teeth_mask)
            plaque_area = np.sum(plaque_on_teeth > 0)
            
            if teeth_area > 0:
                plaque_ratio = plaque_area / teeth_area
            else:
                plaque_ratio = 0.0
            
            # Calculate score
            score = min(1.0, plaque_ratio * 5)
            
            if score < 0.2:
                severity = "None"
            elif score < 0.4:
                severity = "Mild"
            elif score < 0.6:
                severity = "Moderate"
            else:
                severity = "Severe"
            
            return {
                "severity": severity,
                "score": score,
                "plaque_percentage": round(plaque_ratio * 100, 2)
            }
            
        except Exception as e:
            logger.error(f"Error detecting plaque/tartar: {str(e)}")
            return {"severity": "None", "score": 0.0}
    
    def calculate_overall_score(self, yellowness_result: Dict, flaws_result: Dict) -> Dict:
        """Calculate overall dental health score"""
        try:
            # Weight factors
            yellowness_weight = 0.4
            flaws_weight = 0.6
            
            # Convert scores to health scores (invert for negative conditions)
            yellowness_health = 1.0 - yellowness_result["yellowness_score"]
            flaws_health = 1.0 - flaws_result["flaw_score"]
            
            # Calculate weighted average
            overall_score = (yellowness_health * yellowness_weight + 
                           flaws_health * flaws_weight)
            
            # Ensure score is between 0 and 1
            overall_score = max(0.0, min(1.0, overall_score))
            
            # Determine grade
            if overall_score >= 0.9:
                grade = "A+"
            elif overall_score >= 0.8:
                grade = "A"
            elif overall_score >= 0.7:
                grade = "B"
            elif overall_score >= 0.6:
                grade = "C"
            elif overall_score >= 0.5:
                grade = "D"
            else:
                grade = "F"
            
            return {
                "overall_score": round(overall_score, 3),
                "grade": grade,
                "yellowness_contribution": round(yellowness_health * yellowness_weight, 3),
                "flaws_contribution": round(flaws_health * flaws_weight, 3)
            }
            
        except Exception as e:
            logger.error(f"Error calculating overall score: {str(e)}")
            return {
                "overall_score": 0.5,
                "grade": "C",
                "yellowness_contribution": 0.0,
                "flaws_contribution": 0.0
            }
    
    def analyze_dental_image(self, image: Image.Image, user_info: Dict = None) -> Dict:
        """Main function to analyze dental image for yellowness and basic flaws"""
        try:
            # Preprocess image
            processed_image = self.preprocess_image(image)
            
            # Detect teeth regions
            teeth_mask = self.detect_teeth_region(processed_image)
            
            # Analyze yellowness
            yellowness_result = self.analyze_tooth_yellowness(processed_image, teeth_mask)
            
            # Detect basic flaws
            flaws_result = self.detect_basic_dental_flaws(processed_image, teeth_mask)
            
            # Calculate overall score
            overall_result = self.calculate_overall_score(yellowness_result, flaws_result)
            
            # Combine all results
            analysis_result = {
                "timestamp": datetime.now().isoformat(),
                "user_info": user_info or {},
                "teeth_detected": np.sum(teeth_mask) > 1000,  # Minimum pixels for valid detection
                "yellowness_analysis": yellowness_result,
                "flaws_analysis": flaws_result,
                "overall_assessment": overall_result,
                "summary": {
                    "primary_concerns": [],
                    "recommendations": []
                }
            }
            
            # Generate summary
            concerns = []
            recommendations = []
            
            # Add yellowness concerns
            if yellowness_result["yellowness_score"] > 0.3:
                concerns.append(f"Tooth yellowness: {yellowness_result['severity']}")
                recommendations.extend(yellowness_result["recommendations"][:2])
            
            # Add flaw concerns
            if flaws_result["flaw_score"] > 0.3:
                concerns.append(f"Dental flaws: {flaws_result['severity']}")
                recommendations.extend(flaws_result["recommendations"][:2])
            
            # Add to summary
            analysis_result["summary"]["primary_concerns"] = concerns
            analysis_result["summary"]["recommendations"] = list(set(recommendations))  # Remove duplicates
            
            # Store in history
            self.analysis_history.append(analysis_result)
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error in dental analysis: {str(e)}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "teeth_detected": False,
                "yellowness_analysis": {"condition": "error", "yellowness_score": 0.0},
                "flaws_analysis": {"condition": "error", "flaw_score": 0.0},
                "overall_assessment": {"overall_score": 0.0, "grade": "F"},
                "summary": {
                    "primary_concerns": ["Analysis failed"],
                    "recommendations": ["Please retake photo with better lighting"]
                }
            }

# Example usage and testing
if __name__ == "__main__":
    # Initialize the model
    dental_ai = DentalAIModel()
    
    # Example of how to use with a PIL Image
    try:
        # This would be how you'd use it in the Flask app
        from PIL import Image
        
        # Load an example image (replace with actual image path)
        # image = Image.open("dental_image.jpg")
        # result = dental_ai.analyze_dental_image(image)
        
        # Print results
        # print(json.dumps(result, indent=2))
        
        print("Dental AI Model initialized successfully!")
        print("Ready to analyze dental images for yellowness and basic flaws.")
        
    except Exception as e:
        print(f"Error during initialization: {str(e)}")