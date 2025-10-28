import { useState, useCallback } from 'react';
import { 
    createElementWithUpdate, 
    validateElementData, 
    getDefaultFormData 
} from './ElementCreationService';

/**
 * Custom hook for element creation
 * @param {string} version - The version to create elements in
 * @returns {object} Hook state and functions
 */
export const useElementCreation = (version) => {
    const [isCreating, setIsCreating] = useState(false);
    const [lastCreatedElement, setLastCreatedElement] = useState(null);
    const [error, setError] = useState(null);

    /**
     * Create an element
     * @param {string} elementType - The type of element to create
     * @param {object} data - The element data
     * @returns {Promise<object>} The created element
     */
    const createElement = useCallback(async (elementType, data) => {
        setIsCreating(true);
        setError(null);
        
        try {
            // Validate data
            const validation = validateElementData(elementType, data);
            if (!validation.isValid) {
                throw new Error("Validation errors: " + validation.errors.join(", "));
            }

            // Create element
            const element = await createElementWithUpdate(elementType, version, data);
            setLastCreatedElement(element);
            return element;
        } catch (err) {
            setError(err.message);
            throw err;
        } finally {
            setIsCreating(false);
        }
    }, [version]);

    /**
     * Reset the hook state
     */
    const reset = useCallback(() => {
        setIsCreating(false);
        setLastCreatedElement(null);
        setError(null);
    }, []);

    /**
     * Get default form data for an element type
     * @param {string} elementType - The element type
     * @returns {object} Default form data
     */
    const getDefaultData = useCallback((elementType) => {
        return getDefaultFormData(elementType);
    }, []);

    return {
        isCreating,
        lastCreatedElement,
        error,
        createElement,
        reset,
        getDefaultData
    };
}; 